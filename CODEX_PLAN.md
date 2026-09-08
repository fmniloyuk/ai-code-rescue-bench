# CODEX Execution Plan

Source: `CODEX_AUDIT.md` on `master`, auditing baseline commit `6f1021d22957ccdc1977af1d1a2f0909862b770b`.

Prioritization rule: **impact × ease of a safe fix**, not severity alone. A small, contained High-impact correction ranks ahead of a deeper Critical/High change when the latter has materially more implementation or regression risk. Items that would change benchmark semantics/data integrity, public API contracts, external-provider treatment, or require a major isolation redesign are explicitly deferred even when their raw severity/effort would otherwise place them in the Do Now batch.

## Section 3: Human review flags — read before Section 1

The following findings are intentionally **not** in the immediate implementation batch until the product/benchmark contract is confirmed. Their global priority rank is still shown so every audit finding is ranked.

- **Rank 30 — E-01: shared writable workspace across checks (High / Medium).** Fixing this correctly changes evaluation semantics and can change historical scores. Human review should choose the isolation contract first: fresh workspace per check, fresh workspace per stage, or immutable source plus dedicated writable scratch directories, and decide whether the change requires a benchmark methodology/version bump.
- **Rank 31 — E-02: failed generations/invalid patches omitted from experiment artifacts (High / Medium).** Persisting failures is necessary, but the benchmark must first define whether provider errors, malformed patches, and apply failures are zero-score attempts or a separate failure status excluded from task-quality statistics but included in reliability statistics. This affects reported model performance/data integrity.
- **Rank 32 — E-03: `prompt_id` is metadata only (High / Medium).** Making prompt IDs functional changes the exact prompts sent to external providers and therefore changes experiment treatment. Human review should approve the prompt registry/versioning contract and whether existing `default` runs remain comparable.
- **Rank 33 — E-09: unbounded full `/api/runs` response (Medium / Medium).** Pagination or a summary endpoint is warranted, but changing `/api/runs` directly could break the dashboard or external consumers. Prefer an additive compatibility design (`/api/runs/summary` or optional pagination parameters) before implementation.
- **Rank 34 — S-06: candidate can read the mounted hidden grader (High / Large).** A real fix requires architectural isolation for private holdout evaluation (for example a separate grader process/sandbox/service that never mounts grader source into the candidate environment). This is too large and benchmark-semantic-sensitive for the immediate batch.

## Section 1: Do Now

The following 29 findings are ordered by global priority rank. They include every Critical/High Small/Medium finding **except** the four High items above that are deferred by the explicit safety/contract rules, plus safe Medium/Low quick wins.

### 1. Rank 1 — S-04: bound patch size and complexity

**Finding:** Human/model patches have no byte, file, or hunk limit, allowing host memory/disk/processing abuse before Docker limits help.

**Proposed fix:** Add deterministic preflight limits before normalization/workspace creation (maximum patch bytes, changed-file count, and diff/hunk count), reject over-limit attempts with a clear validation error, and add boundary tests for just-under/just-over cases.

**Files likely touched:** `src/rescuebench/patches.py`, `src/rescuebench/evaluator.py`, `tests/test_patches.py`, `docs/SANDBOX_SECURITY.md`.

### 2. Rank 2 — E-04: repair Python public-test invocation

**Finding:** At least six Python-backed public checks execute `python tests/test_public.py`, causing workspace-root imports to fail independently of the submitted patch; the clean reference run demonstrates this with `ModuleNotFoundError: app`.

**Proposed fix:** Change affected public checks to an invocation that preserves the workspace root on import resolution, preferably `python -m pytest -q tests/test_public.py` where the existing script assertions are pytest-compatible; validate every affected deterministic reference and broken baseline after the change.

**Files likely touched:** `benchmarks/py-fastapi-tenant-leak/case.yaml`, `benchmarks/py-async-cache-race/case.yaml`, `benchmarks/py-transaction-outbox/case.yaml`, `benchmarks/py-webhook-idempotency/case.yaml`, `benchmarks/py-resource-leak-stream/case.yaml`, `benchmarks/sql-n-plus-one/case.yaml`, affected public tests only if an invocation-compatible adjustment is genuinely required, `.github/workflows/ci.yml` only if smoke coverage is expanded.

### 3. Rank 3 — T-05: remove the known high-severity npm vulnerability

**Finding:** The exact clean-master install reports one high-severity npm vulnerability and CI accepts it.

**Proposed fix:** Run `npm audit --json` to identify the advisory and dependency path, make the minimum compatible dependency upgrade that removes the High finding, then enforce `npm audit --audit-level=high` (or equivalent JSON assertion) in CI so recurrence fails the build. Avoid `--force` unless a breaking upgrade is reviewed separately.

**Files likely touched:** `web/package.json`, `web/package-lock.json`, `.github/workflows/ci.yml`.

### 4. Rank 4 — S-01: block provider-context symlink host disclosure

**Finding:** Agent-mode provider context reads fixture files on the host before workspace symlink rejection, allowing a hostile fixture symlink to disclose host-file contents to an external LLM.

**Proposed fix:** Move fixture safety validation ahead of any provider-context read and use a single no-follow traversal/validation helper for both context construction and workspace creation. Reject every symlink/special file before reading issue/repository content; add an adversarial test using an external sentinel file to prove it is never read.

**Files likely touched:** `src/rescuebench/context.py`, `src/rescuebench/workspace.py`, `src/rescuebench/cli.py`, new/shared fixture-safety helper if appropriate, `tests/` security tests, `docs/SANDBOX_SECURITY.md`.

### 5. Rank 5 — S-02: bound Docker stdout/stderr while streaming

**Finding:** `capture_output=True` buffers unlimited hostile container output in host memory and only truncates after completion.

**Proposed fix:** Replace whole-process capture with incremental `Popen` pipe draining into fixed-size ring/capped buffers; discard or terminate after a configured output budget while still draining enough to avoid pipe deadlock. Preserve the current last-N-bytes artifact behavior without ever retaining unbounded output in RAM.

**Files likely touched:** `src/rescuebench/sandbox.py`, `tests/test_sandbox.py`, `docs/SANDBOX_SECURITY.md`.

### 6. Rank 6 — S-03: guarantee container cleanup on timeout

**Finding:** A timed-out `docker run` client is not followed by explicit daemon-side container termination/removal.

**Proposed fix:** Give each sandbox run a unique container identity or `--cidfile`; in timeout/error cleanup, issue a trusted host-side `docker rm -f` for exactly that container and remove the cidfile. Add an integration test that times out a long-lived command and verifies no matching container remains.

**Files likely touched:** `src/rescuebench/sandbox.py`, `tests/test_sandbox.py`, `docs/SANDBOX_SECURITY.md`.

### 7. Rank 7 — S-05: cap aggregate provider context

**Finding:** Provider context caps individual files but has no total bytes/files budget.

**Proposed fix:** Add deterministic maximum file-count and aggregate-byte budgets, stop/truncate predictably after sorted traversal, and record that truncation in provider context metadata or prompt text so experiments are auditable. Apply the cap after symlink/special-file rejection from S-01.

**Files likely touched:** `src/rescuebench/context.py`, `src/rescuebench/providers/base.py` if metadata is added, `tests/`, `docs/EVALUATION.md`, `docs/SANDBOX_SECURITY.md`.

### 8. Rank 8 — E-07: persist benchmark provenance with every result

**Finding:** `result.json` lacks enough provenance to reconstruct the exact benchmark treatment/environment.

**Proposed fix:** Add additive provenance fields for benchmark Git SHA, evaluator image identifiers/digests actually used, prompt digest/version, relevant tool/runtime versions, and token-pricing assumptions. Populate them at evaluation time without changing score semantics, and render only useful fields in the dashboard.

**Files likely touched:** `src/rescuebench/models.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/sandbox.py` or a provenance helper, `src/rescuebench/providers/base.py`, `src/rescuebench/artifacts.py`, `web/src/App.tsx`, `docs/EVALUATION.md`, tests.

### 9. Rank 9 — Q-01: add adversarial tests for security-critical boundaries

**Finding:** The highest-risk host/sandbox boundaries have only shallow direct tests.

**Proposed fix:** Add focused regression tests for provider-context symlinks, aggregate context caps, patch-size/path limits, bounded output capture, forced container cleanup, common protected test-file naming, and workspace-side-effect behavior. Prefer cheap unit tests plus a small number of Docker integration tests.

**Files likely touched:** `tests/test_sandbox.py`, `tests/test_patches.py`, new tests for context/workspace/evaluator as needed; no production semantics beyond the corresponding fixes.

### 10. Rank 10 — E-05: make the Semgrep check deterministic within its budget

**Finding:** The tenant reference Semgrep check timed out after the patch, making the deterministic reference score unstable.

**Proposed fix:** Reproduce the rule in the trusted evaluator image, disable unnecessary network/metrics/version-check behavior, scope Semgrep to the intended file/rule, and set a timeout justified by repeated local/CI runs. Require several consecutive reference executions to pass before accepting the adjustment.

**Files likely touched:** `benchmarks/py-fastapi-tenant-leak/case.yaml`, `benchmarks/py-fastapi-tenant-leak/tests_hidden/semgrep.yml`, `docker/python.Dockerfile` only if evaluator configuration/dependency behavior must change, CI smoke assertions.

### 11. Rank 11 — T-01: actually run configured strict mypy

**Finding:** Strict mypy is configured but project-level runner code is not type-checked in local lint or CI.

**Proposed fix:** Add `mypy` for the `rescuebench` package to the canonical lint/check target and CI. Fix only type errors exposed by the already-declared configuration; do not relax strict settings merely to make the gate green.

**Files likely touched:** `Makefile`, `.github/workflows/ci.yml`, source files only if the existing code contains real type errors when this later execution step is performed.

### 12. Rank 12 — T-02: add Node/TypeScript/React evaluator coverage to smoke CI

**Finding:** CI does not build the Node evaluator image or execute any TS/React fixture.

**Proposed fix:** Build all trusted images through the canonical image-builder and add one fast deterministic Node/TypeScript or React reference case to the smoke set, asserting both broken-baseline failure and repaired reference success.

**Files likely touched:** `.github/workflows/ci.yml`, `scripts/assert-reference-results.py` if the expected-case set grows; use existing benchmark fixtures/images rather than duplicating them.

### 13. Rank 13 — T-06: commit and enforce the npm lockfile

**Finding:** CI regenerates a lockfile before `npm ci`, so transitive versions are not reproducible.

**Proposed fix:** Commit `web/package-lock.json` generated from the reviewed dependency set, replace the CI install sequence with plain `npm ci`, and keep Dependabot/npm audit operating against the committed lock.

**Files likely touched:** `web/package-lock.json`, `.github/workflows/ci.yml`, `web/package.json` only if T-05 requires an upgrade.

### 14. Rank 14 — E-08: sort run artifacts by `created_at`

**Finding:** Run lists are sorted lexically by random run-directory name rather than chronology.

**Proposed fix:** Parse results first, sort valid results by timezone-aware `created_at` descending, and add deterministic tests proving cross-case/random UUID names cannot reorder the newest run.

**Files likely touched:** `src/rescuebench/artifacts.py`, new `tests/test_artifacts.py`, potentially `web/src/App.tsx` only if it currently compensates for ordering.

### 15. Rank 15 — E-12: include important non-suffix configuration files in model context

**Finding:** Agent snapshots omit `Dockerfile`, `Makefile`, shell scripts, lockfiles, and similar repair-relevant text.

**Proposed fix:** Replace the suffix-only rule with a documented allowlist of well-known text filenames plus safe text suffixes, adding `.sh` and lock/config names needed by existing cases. Reuse S-01/S-05 safety and aggregate-size controls so broader context does not reopen disclosure/DoS risk.

**Files likely touched:** `src/rescuebench/context.py`, tests, `docs/EVALUATION.md`.

### 16. Rank 16 — E-06: preserve generation latency separately from evaluation runtime

**Finding:** Provider adapters calculate latency but the result discards it, and evaluation runtime starts after generation.

**Proposed fix:** Add backward-compatible result fields such as `generation_latency_ms`, `evaluation_runtime_ms`, and derived/recorded total wall time; populate agent and human modes consistently and expose them in comparisons without rewriting existing artifacts.

**Files likely touched:** `src/rescuebench/models.py`, `src/rescuebench/cli.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/providers/*`, `web/src/App.tsx`, tests/docs.

### 17. Rank 17 — U-01: prevent stale dashboard case-detail responses

**Finding:** Rapid selection changes can render case details from an older fetch under the newly selected run.

**Proposed fix:** Add an `AbortController` or monotonically increasing request token to the selected-run effect and ignore aborted/stale responses in cleanup. Reset detail state only for the active request.

**Files likely touched:** `web/src/App.tsx`, frontend tests introduced under Q-02.

### 18. Rank 18 — S-07: harden protected test/control path detection

**Finding:** Current path rules miss common JS/TS test layouts such as `*.test.ts`, `*.spec.ts` and `__tests__`.

**Proposed fix:** Centralize protected-path matching and cover conventional test directories/files across Python/JS/TS plus benchmark control files; reject patches that touch them before workspace creation. Add table-driven tests for allowed and denied paths.

**Files likely touched:** `src/rescuebench/patches.py`, `tests/test_patches.py`, `docs/SANDBOX_SECURITY.md`.

### 19. Rank 19 — T-07: add Python dependency vulnerability/reproducibility controls

**Finding:** Host Python dependencies are broad-range resolved and there is no Python vulnerability gate.

**Proposed fix:** Add `pip-audit` (or equivalent) to CI with an explicit severity/failure policy, and generate a reviewed constraints/lock artifact for development/CI dependencies while keeping published package metadata appropriately ranged. Document how evaluator-image dependencies are updated separately.

**Files likely touched:** `pyproject.toml`, constraints/lock file, `.github/workflows/ci.yml`, `Makefile`, relevant Dockerfiles if exact evaluator pins are coordinated with T-08, docs.

### 20. Rank 20 — T-08: pin evaluator execution environment

**Finding:** Docker base tags and some evaluator packages are mutable/range-resolved, weakening benchmark reproducibility.

**Proposed fix:** Pin the currently reviewed base images by digest and evaluator packages by exact versions, record the resulting image ID/digest in provenance (E-07), and let Dependabot propose deliberate upgrades instead of floating at build time.

**Files likely touched:** `docker/python.Dockerfile`, `docker/node.Dockerfile`, `docker/config.Dockerfile`, `docker/patcher.Dockerfile`, `docs/SANDBOX_SECURITY.md`, `.github/dependabot.yml` only if update policy needs refinement.

### 21. Rank 21 — Q-02: close direct test gaps in API/artifact/CLI/provider/frontend paths

**Finding:** The root suite has only six tests and no direct coverage for API routes, ArtifactStore behavior, provider adapters, key evaluator errors, or the dashboard.

**Proposed fix:** Add FastAPI route tests, ArtifactStore ordering/corruption tests, CLI error-path tests, provider-adapter tests with mocked HTTP, evaluator failure tests, and a minimal Vitest/React Testing Library dashboard suite covering fetch state/races. Introduce coverage reporting as visibility, not as an arbitrary high threshold initially.

**Files likely touched:** `tests/` new files, `web/package.json`, `web/package-lock.json`, `web/src/App.tsx` only for testability/fixes already planned, CI.

### 22. Rank 22 — S-08: stop exposing absolute host paths

**Finding:** API/results expose absolute filesystem paths for case and artifact locations.

**Proposed fix:** Preserve existing field names/types for compatibility but serialize repository-relative/logical paths (for example `benchmarks/<id>` and `artifacts/runs/<id>`) rather than host absolute paths; keep internal `Path` objects private to execution code.

**Files likely touched:** `src/rescuebench/models.py`, `src/rescuebench/catalog.py`, `src/rescuebench/evaluator.py`, tests; API schema should remain additive/compatible.

### 23. Rank 23 — E-11: make reference-result selection deterministic

**Finding:** The assertion script overwrites duplicate case entries in unspecified glob order.

**Proposed fix:** Parse matching artifacts with timestamps and either require exactly one current-run artifact per expected case or explicitly choose the newest by `created_at`; fail loudly on ambiguous duplicates rather than relying on filesystem order.

**Files likely touched:** `scripts/assert-reference-results.py`, script tests if added, `.github/workflows/ci.yml` only if artifacts are placed in a dedicated smoke directory.

### 24. Rank 24 — U-02: clear stale dashboard error state after recovery

**Finding:** A transient API error can remain visible after subsequent requests succeed.

**Proposed fix:** Clear the relevant error at the start of a new request and/or after a successful response, while ignoring abort-related errors from U-01.

**Files likely touched:** `web/src/App.tsx`, frontend tests.

### 25. Rank 25 — T-03: use one evaluator-image build definition

**Finding:** Makefile, shell script and CI duplicate image-build commands and have drifted.

**Proposed fix:** Treat `scripts/build-evaluator-images.sh` as the single canonical builder; make `make images` and CI call it rather than restating the four builds. Keep image tags defined in one place where practical.

**Files likely touched:** `Makefile`, `scripts/build-evaluator-images.sh`, `.github/workflows/ci.yml`.

### 26. Rank 26 — T-04: align local and CI Ruff scope

**Finding:** `make lint` omits `scripts`, while CI includes it.

**Proposed fix:** Make the local target execute the exact CI Ruff scope (`src tests tools scripts`) or have both call a single canonical check target/script.

**Files likely touched:** `Makefile`, possibly `.github/workflows/ci.yml` if centralizing commands.

### 27. Rank 27 — T-09: remove deprecated GitHub Actions runtime warnings

**Finding:** Current pinned action majors target the deprecated Node 20 action runtime on current hosted runners.

**Proposed fix:** Upgrade each first-party action to the current Node-24-compatible supported release after checking its migration notes, retaining the same permissions/cache/artifact behavior; pin by full commit SHA if the repository adopts stronger supply-chain controls.

**Files likely touched:** `.github/workflows/ci.yml`.

### 28. Rank 28 — T-10: fix `doctor()` exit handling

**Finding:** `typer.Exit("Docker daemon is unavailable")` passes a string where an integer exit code is expected.

**Proposed fix:** Print the diagnostic through Rich/Typer, then raise `typer.Exit(code=1)`. Add a CLI test with a mocked failed Docker version command.

**Files likely touched:** `src/rescuebench/cli.py`, CLI tests.

### 29. Rank 29 — E-10: make artifact persistence atomic and corruption visible

**Finding:** Partial writes can be silently skipped and disappear from comparisons.

**Proposed fix:** Write JSON/patch to temporary files in the target filesystem, flush/close, then `os.replace` atomically; when listing, surface invalid artifacts through logging/diagnostics rather than silently swallowing them. Add interruption/corrupt-file tests.

**Files likely touched:** `src/rescuebench/artifacts.py`, `tests/test_artifacts.py`, potentially CLI/API diagnostics if corruption is exposed there.

## Section 2: Deferred

The following five findings remain ranked but are deferred under the explicit rules in the prompt.

1. **Rank 30 — E-01: isolate check workspaces (High / Medium).** **Deferred because it changes benchmark execution semantics and historical score/data-integrity comparability.** Approve an isolation/versioning contract first, then implement with a benchmark methodology version bump if required.
2. **Rank 31 — E-02: persist failed model/provider attempts (High / Medium).** **Deferred because deciding whether failures score zero or live in a separate reliability denominator changes benchmark data semantics.** Define the statistical/reporting contract before changing stored results.
3. **Rank 32 — E-03: make prompt IDs functional (High / Medium).** **Deferred because it deliberately changes external LLM prompt behavior/treatment.** Approve a versioned prompt registry and migration policy before sending different prompts under existing/new IDs.
4. **Rank 33 — E-09: paginate/summarize `/api/runs` (Medium / Medium).** **Deferred because a direct response-shape change could break the public API/dashboard contract.** Design an additive summary/pagination endpoint or backward-compatible optional parameters first.
5. **Rank 34 — S-06: isolate private hidden graders from candidate code (High / Large).** **Deferred because it requires a Large architectural security redesign.** Private holdout execution should be designed as a separate trust domain rather than patched into the current shared-container model.

## Execution sequencing note

Within the Do Now batch, implement in small reviewable groups rather than one large patch:

1. **Restore trustworthy green baseline:** E-04, E-05, T-01, T-02, T-03, T-04, T-06, T-10.
2. **Close host-boundary abuse paths:** S-04, S-01, S-02, S-03, S-05, S-07, Q-01.
3. **Strengthen reproducibility/results:** E-07, E-08, E-06, E-10, E-11, S-08, T-07, T-08.
4. **Improve agent/dashboard correctness:** E-12, U-01, U-02, Q-02.
5. **Dependency/CI maintenance:** T-05 and T-09 can be landed independently as soon as their exact advisories/migration notes are verified.

Each group should preserve the original audit baseline in `CODEX_AUDIT.md`; after implementation, record a separate “after” verification rather than rewriting the before numbers.