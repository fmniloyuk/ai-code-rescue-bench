# CODEX Audit

Audit target: `master` at commit `6f1021d22957ccdc1977af1d1a2f0909862b770b` (tree `c8c0710387eec0f32f26d4fe5f50633c524acbbb`).

This is an investigation-only audit. No source code was changed while establishing the baseline or reviewing the code. Baseline execution data below comes from the clean GitHub Actions `master` push run for that exact commit on 2026-09-08 (workflow run `34223996286`).

## Section 1: Architecture & tooling summary

### 1.1 Repository architecture

`ai-code-rescue-bench` is a filesystem-backed benchmark/evaluation platform rather than a conventional CRUD application. Its primary execution path is:

```text
Human patch OR LLM provider
        |
        v
Typer CLI (`rescuebench`)
        |
        +--> BenchmarkCatalog -> benchmarks/<case>/case.yaml + issue.md + repo/
        |
        +--> agent mode: provider-context snapshot -> provider adapter -> unified diff
        |
        v
Evaluator
  1. normalize/validate patch
  2. create disposable fixture workspace
  3. run broken baseline checks in constrained Docker containers
  4. apply patch in trusted patcher container
  5. run repaired checks in constrained Docker containers
  6. deterministic scoring
        |
        v
ArtifactStore -> artifacts/runs/<run-id>/{result.json,attempt.patch}
        |
        v
FastAPI read-only API
        |
        v
React/Vite dashboard
```

There is **no production database layer** in the benchmark platform itself. Benchmark definitions and broken fixtures are version-controlled files; evaluation results are JSON/patch files under `artifacts/runs/`. PostgreSQL/SQL appears inside benchmark cases and trusted evaluators, not as the platform's persistence layer.

### 1.2 Backend / runner modules

Language: **Python 3.13+**.

Frameworks/libraries: **Typer**, **FastAPI**, **Pydantic v2**, **pydantic-settings**, **httpx**, **PyYAML**, **Rich**, **Uvicorn**.

Primary package: `src/rescuebench/`.

| Module | Responsibility |
|---|---|
| `src/rescuebench/cli.py` | Typer CLI entry point; human evaluation, agent evaluation, comparison, doctor, API server. |
| `src/rescuebench/catalog.py` | Finds and validates benchmark manifests. |
| `src/rescuebench/context.py` | Builds the repository snapshot and issue context supplied to model providers. |
| `src/rescuebench/providers/base.py` | Provider protocol/context/proposal abstractions. |
| `src/rescuebench/providers/openai_compat.py` | OpenAI-compatible Chat Completions adapter. |
| `src/rescuebench/providers/anthropic.py` | Anthropic Messages API adapter. |
| `src/rescuebench/providers/mock.py` | Deterministic offline demonstration provider backed by checked-in `mock.patch`. |
| `src/rescuebench/evaluator.py` | Baseline/repair evaluation orchestration and artifact creation. |
| `src/rescuebench/workspace.py` | Temporary attempt workspace construction and fixture symlink rejection. |
| `src/rescuebench/patches.py` | Diff normalization, protected-path checks, changed-line counting, sandboxed `git apply`. |
| `src/rescuebench/sandbox.py` | Docker command construction, resource/security flags, timeouts and result capture. |
| `src/rescuebench/scoring.py` | Deterministic weighted score and regression/changed-lines penalties. |
| `src/rescuebench/artifacts.py` | Filesystem persistence/retrieval of run artifacts. |
| `src/rescuebench/models.py` | Pydantic schemas for cases, checks, proposals, results and scores. |
| `src/rescuebench/api.py` | Read-only FastAPI endpoints for cases and run artifacts. |

Python package entry point from `pyproject.toml`:

```text
rescuebench = rescuebench.cli:app
```

FastAPI application entry point:

```text
rescuebench.api:app
```

API routes present:

- `GET /api/health`
- `GET /api/cases`
- `GET /api/cases/{case_id}`
- `GET /api/runs`
- `GET /api/runs/{run_id}`

No duplicate API routes were found. The API is intentionally read-only. CORS is limited to `http://localhost:5173`, GET requests, and does not enable credentials.

### 1.3 Frontend

Language: **TypeScript / TSX**.

Frameworks: **React 19.1.1**, **React DOM 19.1.1**, **Vite 7.1.3**, **TypeScript 5.9.2**.

Location: `web/`.

Entry point: `web/src/main.tsx`, rendering `web/src/App.tsx`.

The dashboard calls the read-only backend through `/api`; Vite proxies `/api` to `http://127.0.0.1:8000`. It displays benchmark metadata, run/check details, diffs, scores, timing, model/provider metadata and grouped repeated-trial summaries.

No frontend test framework or frontend linter is configured. TypeScript compilation is the configured static check for dashboard source.

### 1.4 Benchmark data set

Location: `benchmarks/<case-id>/`.

There are **16 validated benchmark manifests** spanning:

- Python / FastAPI / asyncio
- Node.js / TypeScript
- React / TypeScript
- SQL / PostgreSQL patterns
- Docker Compose / configuration

A case generally contains:

```text
case.yaml
issue.md
repo/                 # broken fixture and visible checks
repo/tests/
tests_hidden/         # evaluator-only checks
mock.patch            # deterministic reference demonstration
```

The runner uses trusted local evaluator images:

- `rescuebench/patcher:local`
- `rescuebench/python:local`
- `rescuebench/node:local`
- `rescuebench/config:local`

Dockerfiles are under `docker/`; `scripts/build-evaluator-images.sh` also builds all four.

### 1.5 Package managers and local commands

#### Python / runner

Install development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Build evaluator images:

```bash
make images
# or
./scripts/build-evaluator-images.sh
```

Check Docker availability/policy:

```bash
rescuebench doctor
```

List cases:

```bash
rescuebench list
```

Run a deterministic mock attempt:

```bash
rescuebench agent py-fastapi-tenant-leak --provider mock
```

Evaluate a human patch:

```bash
rescuebench evaluate py-fastapi-tenant-leak --patch ./my-fix.patch
```

Run the API:

```bash
rescuebench serve
# default: 127.0.0.1:8000
```

Configured Python unit tests:

```bash
pytest
```

Configured Ruff lint used by CI:

```bash
ruff check src tests tools scripts
```

`make lint` currently runs a slightly different command and omits `scripts`:

```bash
ruff check src tests tools
```

Strict mypy is configured in `pyproject.toml`, and the expected project-level command is:

```bash
mypy
```

However, neither `make lint` nor the current CI executes project-level mypy; this is recorded as a finding below.

#### Dashboard

From `web/`:

```bash
npm install
npm run dev
npm run typecheck
npm run build
```

CI currently installs with:

```bash
npm install --package-lock-only && npm ci
```

There is no committed `web/package-lock.json`, so CI regenerates dependency resolution before `npm ci`; this is recorded as a reproducibility finding.

### 1.6 Review areas with no defect found

The full-tree review/search did **not** identify:

- unresolved `TODO`, `FIXME`, `XXX`, or `HACK` markers;
- duplicate FastAPI routes/endpoints;
- a second/abandoned product name or obvious half-finished rebrand;
- exposed private keys or obvious `sk-...` API secrets in tracked source;
- permissive wildcard CORS;
- unsafe YAML deserialization (`yaml.safe_load` is used);
- fabricated commercial-model benchmark results; the deterministic mock provider is explicit and documented as a test/demo path.

Intentional defects inside `benchmarks/*/repo` are benchmark data and are not counted as platform bugs unless the evaluator harness itself prevents the fixture from being evaluated correctly.

## Section 2: Baseline test/lint results

Baseline revision: `master` commit `6f1021d22957ccdc1977af1d1a2f0909862b770b`.

Clean baseline source: GitHub Actions push workflow run `34223996286`, created immediately after that exact merge commit on 2026-09-08.

### 2.1 Python core

Install command:

```bash
python -m pip install -e '.[dev]'
```

Runner Python in CI: **CPython 3.13.15**.

Ruff command:

```bash
ruff check src tests tools scripts
```

Result:

- **0 violations**
- output: `All checks passed!`

Pytest command:

```bash
pytest
```

Result:

- **6 passed**
- **0 failed**
- **0 errors**
- duration: **0.16s**

Catalog validation:

- **16 manifests validated**
- duplicate-id assertion passed
- **0 manifest validation failures**

Project-level mypy:

- strict mypy is configured in `pyproject.toml`;
- **not executed by the current clean-master CI or Makefile**, therefore there is no honest project-level baseline pass/fail count to report from the available execution record;
- fixture-level mypy does run inside applicable benchmark checks, but that is not a substitute for type-checking `src/rescuebench`.

### 2.2 Dashboard

CI environment:

- Node.js **22.23.2**
- npm **10.9.8**

Install/audit command executed:

```bash
npm install --package-lock-only && npm ci
```

Dependency audit result:

- first resolution: **120 packages audited, 1 high-severity vulnerability**;
- installed tree: **71 packages audited, 1 high-severity vulnerability**;
- CI did not fail on the vulnerability.

Build/type-check command:

```bash
npm run build
# expands to: tsc -b && vite build
```

Result:

- TypeScript: **0 reported compile/type errors**
- Vite build: **success**
- **29 modules transformed**
- production build completed in **919ms**
- frontend test count: **0** because no test command/framework is configured
- frontend lint count: **not applicable** because no frontend linter command/config is present

### 2.3 Sandboxed benchmark smoke baseline

Commands:

```bash
rescuebench doctor
rescuebench agent py-fastapi-tenant-leak --provider mock --json
rescuebench agent docker-service-localhost --provider mock --json
python scripts/assert-reference-results.py py-fastapi-tenant-leak docker-service-localhost
```

Docker doctor result:

- Docker server **28.0.4**
- doctor command passed

`py-fastapi-tenant-leak` deterministic reference attempt:

- final score: **77/100** — unexpected failure for a reference mock
- changed lines: **6**
- repaired checks: **8 passed, 2 failed**
- failed repaired public check: `ModuleNotFoundError: No module named 'app'`
- failed repaired Semgrep check: **timeout**, exit **124**, **30,012ms**
- baseline checks: **5 passed, 5 failed**
- result validation therefore failed because the reference mock did not score 100

`docker-service-localhost` deterministic reference attempt:

- final score: **100/100**
- changed lines: **2**
- repaired checks: **7 passed, 0 failed**
- broken baseline contained expected failures and was confirmed by the assertion script

Smoke-job summary:

- reference cases attempted: **2**
- references meeting the expected 100-point contract: **1**
- references failing that contract: **1**
- final assertion step: **failed**

### 2.4 Overall clean-master CI baseline

Jobs:

- `Core tests and catalog`: **PASS**
- `Dashboard build`: **PASS**
- `Sandboxed benchmark smoke`: **FAIL**

Overall workflow: **FAIL**.

## Section 3: Findings

### A. Security & sandbox boundary

| ID | File path(s) | Description | Severity | Effort |
|---|---|---|---|---|
| S-01 | `src/rescuebench/context.py`, `src/rescuebench/cli.py`, `src/rescuebench/workspace.py` | **Host-file disclosure before symlink validation.** Agent mode builds provider context by calling `repo.rglob()`, `is_file()` and `read_text()` on fixture files on the host. Fixture symlinks are rejected only later, when `create_workspace()` runs after provider generation. A hostile fixture can therefore symlink a text-looking path to a readable host file and cause its contents to be copied into an external LLM request. This directly violates the documented assumption that benchmark repositories are untrusted. | **Critical** | **Medium** |
| S-02 | `src/rescuebench/sandbox.py`, `docs/SANDBOX_SECURITY.md` | **Unbounded host-memory capture from hostile stdout/stderr.** `subprocess.run(..., capture_output=True)` buffers all Docker output in host memory, then truncates to 50 KB only after the process exits. The container memory limit does not bound the host pipe buffer accumulated by Python. A benchmark can print indefinitely and exhaust host memory. Documentation currently says captured output is bounded, which is not true at capture time. | **Critical** | **Medium** |
| S-03 | `src/rescuebench/sandbox.py` | **Timeout does not explicitly terminate the Docker container.** `TimeoutExpired` terminates the local `docker run` client, but the code has no `--cidfile`/container name plus `docker rm -f` cleanup path. A daemon-managed container can outlive the client and continue consuming CPU/memory after the evaluator reports timeout. | **High** | **Medium** |
| S-04 | `src/rescuebench/patches.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/artifacts.py` | **No patch size/file/hunk limit.** Human/model patches are normalized, held in host memory, written to disk and passed to `git apply` without an upper byte/file count. An oversized untrusted proposal can consume host memory/disk/processing time before sandbox resource limits provide protection. | **High** | **Small** |
| S-05 | `src/rescuebench/context.py` | **Provider context has only a per-file 40 KB cap, not a total byte/file cap.** A hostile fixture can include thousands of allowed text files, causing large host memory use and an unexpectedly large/costly external provider request. | **High** | **Medium** |
| S-06 | `src/rescuebench/evaluator.py`, `docs/SANDBOX_SECURITY.md`, `docs/EVALUATION.md` | **Hidden grader is runtime-readable by candidate code.** `/grader` is mounted read-only, but the candidate code and hidden test run in the same container/process namespace. A malicious candidate can read the private grader during hidden/security execution and branch on or copy its contents. Public-source hidden tests are already visible on GitHub, but this design cannot safely support the private holdout recommended by the docs. | **High** | **Large** |
| S-07 | `src/rescuebench/patches.py` | **Protected-test path heuristic is naming-dependent and incomplete.** It blocks a path component equal to `tests` or starting with `test_`, but common names such as `foo.test.ts`, `foo.spec.ts`, `test.js`, or `__tests__` can fall outside that rule. A future fixture using those layouts could let an attempt alter visible evaluator controls. | **Medium** | **Medium** |
| S-08 | `src/rescuebench/models.py`, `src/rescuebench/catalog.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/api.py` | Case summaries/results serialize absolute host paths (`CaseSummary.path`, `EvaluationResult.artifact_dir`) and expose them through the API/dashboard. This is unnecessary host-environment disclosure and harms artifact portability. | **Low** | **Small** |

### B. Evaluation correctness, benchmark integrity & reproducibility

| ID | File path(s) | Description | Severity | Effort |
|---|---|---|---|---|
| E-01 | `src/rescuebench/evaluator.py`, `src/rescuebench/workspace.py` | **Checks share one writable workspace.** All baseline checks run sequentially against the same writable directory; the patch is then applied to that already-executed baseline workspace; all repaired checks also share it. Candidate/import side effects or test scripts can persist source/state changes across checks, contaminating later hidden/security results and even the pre-patch baseline. | **High** | **Medium** |
| E-02 | `src/rescuebench/cli.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/providers/*`, `docs/EVALUATION.md` | **Failed generations/invalid patches are omitted from experiment artifacts.** Provider errors, empty/malformed diffs, path-validation failures and patch-apply failures raise before a normal `EvaluationResult` is persisted. Repeated-trial comparisons can therefore silently exclude exactly the model failures that should count against reliability, conflicting with the documentation's “preserve every raw artifact” guidance. | **High** | **Medium** |
| E-03 | `src/rescuebench/context.py`, `src/rescuebench/providers/base.py`, `src/rescuebench/cli.py`, `docs/EVALUATION.md`, `web/src/App.tsx` | **`--prompt-id` is non-functional treatment metadata.** `prompt_id` is stored and used for grouping, but `build_prompt()` does not vary the prompt from that id. Two runs can be labeled as different prompt experiments while receiving the same generated prompt, making prompt comparison misleading. | **High** | **Medium** |
| E-04 | `benchmarks/py-fastapi-tenant-leak/case.yaml`, `benchmarks/py-async-cache-race/case.yaml`, `benchmarks/py-transaction-outbox/case.yaml`, `benchmarks/py-webhook-idempotency/case.yaml`, `benchmarks/py-resource-leak-stream/case.yaml`, `benchmarks/sql-n-plus-one/case.yaml`, corresponding `repo/tests/test_public.py` | **At least six Python-backed public checks invoke `python tests/test_public.py` while importing modules from the workspace root.** Direct script execution sets `sys.path[0]` to `/workspace/tests`, so imports such as `from app import ...`, `from cache import ...`, and `from service import ...` fail independently of the submitted repair. The clean master smoke run proves this for `py-fastapi-tenant-leak`, making its public 20 points unattainable even for the deterministic reference patch. | **High** | **Small** |
| E-05 | `benchmarks/py-fastapi-tenant-leak/case.yaml`, `benchmarks/py-fastapi-tenant-leak/tests_hidden/semgrep.yml`, `docker/python.Dockerfile` | The reference tenant-repair Semgrep quality check timed out at the 30-second sandbox limit after the patch, while the baseline Semgrep invocation completed in about 2.3s. This creates nondeterministic reference scoring and contributed 3 lost points in the clean-master smoke run. | **Medium** | **Small** |
| E-06 | `src/rescuebench/models.py`, `src/rescuebench/providers/openai_compat.py`, `src/rescuebench/providers/anthropic.py`, `src/rescuebench/evaluator.py`, `web/src/App.tsx` | Provider adapters populate `PatchProposal.latency_ms`, but `EvaluationResult` does not persist it, and evaluator runtime starts only after provider generation. Model-generation latency is therefore discarded even though the UI/README advertise runtime/model comparison. | **Medium** | **Small** |
| E-07 | `src/rescuebench/models.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/providers/base.py`, `docs/EVALUATION.md` | Run artifacts do not automatically capture key reproducibility provenance recommended by the project's own reporting checklist: benchmark Git SHA, evaluator image digest/ID, actual prompt text or digest, tool/runtime versions, and token-price assumptions. A `result.json` alone cannot reconstruct the exact treatment/environment. | **High** | **Medium** |
| E-08 | `src/rescuebench/artifacts.py`, `src/rescuebench/cli.py`, `web/src/App.tsx` | `ArtifactStore.list()` sorts result file paths by run-directory name, not `created_at`. Run IDs begin with case id plus random UUID, so “first/latest” presentation and limited comparisons are not chronological. | **Medium** | **Small** |
| E-09 | `src/rescuebench/artifacts.py`, `src/rescuebench/api.py`, `web/src/App.tsx` | `/api/runs` reads, validates and returns every full `result.json` including patches/check details with no pagination or summary representation. Runtime and response size grow without bound as experiments accumulate. | **Medium** | **Medium** |
| E-10 | `src/rescuebench/artifacts.py` | Artifact writes are non-atomic and corrupt/partial result files are silently skipped by `list()`. A process interruption can leave a partially written run that disappears from comparisons without any warning. | **Low** | **Medium** |
| E-11 | `scripts/assert-reference-results.py` | The reference assertion stores one result per case by overwriting a dictionary while iterating an unspecified `glob()` order. If multiple artifacts for the same case are present, which run is validated is not explicitly defined. | **Low** | **Small** |
| E-12 | `src/rescuebench/context.py` | Provider repository snapshots are suffix-allowlisted and omit important text files with no/other suffixes, including `Dockerfile`, `Makefile`, `.sh`, lockfiles and other configuration. Agent-mode repairs can therefore receive incomplete repository context for configuration-oriented cases. | **Medium** | **Small** |

### C. Frontend correctness

| ID | File path(s) | Description | Severity | Effort |
|---|---|---|---|---|
| U-01 | `web/src/App.tsx` | The selected-run case-detail effect has no `AbortController` or request-generation guard. Rapid run changes can allow an older `/api/cases/{id}` response to arrive later and overwrite `caseDetail`, rendering issue metadata for the wrong selected run. | **Medium** | **Small** |
| U-02 | `web/src/App.tsx` | The top-level `error` state is set on fetch failure but not consistently cleared after a later successful fetch, so a transient backend error can leave a stale error banner after data has recovered. | **Low** | **Small** |

### D. CI, dependency & developer-tooling issues

| ID | File path(s) | Description | Severity | Effort |
|---|---|---|---|---|
| T-01 | `pyproject.toml`, `Makefile`, `.github/workflows/ci.yml` | Strict mypy is configured for `rescuebench`, but project-level mypy is never run by `make lint` or CI. Type errors in the runner can merge despite a declared strict configuration. | **Medium** | **Small** |
| T-02 | `.github/workflows/ci.yml`, `docker/node.Dockerfile` | PR/master smoke CI builds only patcher, Python and config evaluator images and evaluates only Python + Docker cases. It neither builds `rescuebench/node:local` nor runs a TypeScript/React fixture, so a broken Node evaluator/toolchain can merge unnoticed. | **Medium** | **Small** |
| T-03 | `Makefile`, `scripts/build-evaluator-images.sh`, `.github/workflows/ci.yml` | Evaluator-image build commands are duplicated in three places and have already drifted: the script/Makefile build all four images while CI omits Node. | **Low** | **Small** |
| T-04 | `Makefile`, `.github/workflows/ci.yml` | Local `make lint` checks `src tests tools`, while CI checks `src tests tools scripts`. Local lint can pass for code that will fail CI. | **Low** | **Small** |
| T-05 | `web/package.json`, `.github/workflows/ci.yml` | The clean-master npm install/audit reports **1 high-severity vulnerability**. CI records the warning but does not enforce an audit threshold, so a known high-severity dependency issue is currently accepted. | **High** | **Small** |
| T-06 | `web/package.json`, `.github/workflows/ci.yml` | No `web/package-lock.json` is committed. CI first runs `npm install --package-lock-only` and only then `npm ci`, so transitive dependency resolution can change between runs despite using `npm ci`. | **Medium** | **Small** |
| T-07 | `pyproject.toml`, `docker/python.Dockerfile`, `docker/config.Dockerfile`, `.github/workflows/ci.yml` | Python dependencies use broad ranges and there is no `pip-audit`/equivalent vulnerability gate or committed lock/constraints set for the host runner. The exact installed host dependency set can drift; evaluator images also leave several dependencies range-resolved at build time. | **Medium** | **Medium** |
| T-08 | `docker/python.Dockerfile`, `docker/node.Dockerfile`, `docker/config.Dockerfile`, `docker/patcher.Dockerfile`, `docs/SANDBOX_SECURITY.md` | Evaluator base images are referenced by mutable tags in source and several package installs use version ranges. CI logs show resolved image digests, but those digests are not declared in the benchmark revision/result, weakening supply-chain and benchmark reproducibility. The documentation acknowledges this limitation. | **Medium** | **Medium** |
| T-09 | `.github/workflows/ci.yml` | Current Actions versions (`checkout@v4`, `setup-python@v5`, `setup-node@v4`, `upload-artifact@v4`) emit GitHub-hosted-runner warnings because they target the deprecated Node 20 action runtime and are being forced onto Node 24. | **Low** | **Small** |
| T-10 | `src/rescuebench/cli.py` | `doctor()` raises `typer.Exit("Docker daemon is unavailable")`, but Typer/Click's exit API expects an integer exit code. The error message should be printed separately and `typer.Exit(code=1)` used. Project-level strict mypy is not currently run, so this misuse is not caught by CI. | **Low** | **Small** |

### E. Test-coverage gaps

No coverage tool/report is configured, so exact line/branch coverage percentages cannot be stated without inventing numbers. The following are direct, observable gaps in the tracked tests.

| ID | File path(s) | Description | Severity | Effort |
|---|---|---|---|---|
| Q-01 | `tests/test_sandbox.py`, `tests/test_patches.py`, `src/rescuebench/context.py`, `src/rescuebench/sandbox.py`, `src/rescuebench/workspace.py`, `src/rescuebench/evaluator.py` | Security-critical boundaries have only shallow direct tests. There is no test for provider-context symlink handling, aggregate context caps, bounded output capture, forced container cleanup after timeout, workspace cross-check contamination, protected JS test-name variants, or patch-size rejection. These are the same areas where the highest-severity findings exist. | **High** | **Medium** |
| Q-02 | `src/rescuebench/api.py`, `src/rescuebench/artifacts.py`, `src/rescuebench/cli.py`, `src/rescuebench/context.py`, `src/rescuebench/evaluator.py`, `src/rescuebench/workspace.py`, `src/rescuebench/providers/*`, `web/src/App.tsx`, `tests/` | There are no direct automated tests for the five FastAPI routes, artifact-store ordering/corruption behavior, CLI failure paths, external provider adapters, most evaluator error paths, or the React dashboard. Existing root tests total only six; the two-case Docker smoke test provides useful integration coverage but does not cover these modules/failure modes. | **Medium** | **Medium** |

## Section 4: Total counts

Total findings: **34**.

| Severity | Count |
|---|---:|
| Critical | **2** |
| High | **11** |
| Medium | **13** |
| Low | **8** |
| **Total** | **34** |

Highest-priority themes:

1. Close host/sandbox boundary gaps before treating benchmark fixtures as genuinely untrusted.
2. Restore benchmark-harness correctness so reference repairs can actually achieve their declared score.
3. Prevent failed model attempts and mislabeled prompt experiments from biasing comparisons.
4. Improve result provenance/isolation so published benchmark numbers are reproducible and defensible.
5. Raise CI coverage across the Node/React stack and enforce dependency/type-check gates already implied by the repository configuration.
