# Benchmark Design

## Objective

`ai-code-rescue-bench` measures repair behavior, not code-review eloquence. An attempt succeeds when a submitted patch changes the broken fixture so that independently declared deterministic contracts pass without creating unacceptable regressions.

The unit of evaluation is a **case**, not a free-form repository scan.

## Design principles

### Realistic failure mechanisms

Cases model failures that routinely survive superficial review: tenant leakage, authorization ordering, async races, transaction/outbox ordering, webhook replay, cache invalidation, N+1 access, lost updates, React lifecycle mistakes, resource cleanup, ESM/toolchain mismatches, and container service/readiness errors.

A case is rejected if its main challenge is merely syntax, trivia, or locating an obvious typo.

### Small, heterogeneous benchmark

The project intentionally contains a curated set of 16 cases instead of hundreds of near-duplicates. Diversity of reasoning is more valuable here than inflated item count.

The current set spans:

- Python / FastAPI / asyncio;
- Node.js / TypeScript;
- React lifecycle behavior;
- PostgreSQL query and transaction semantics;
- Docker Compose service discovery/readiness.

### Behavioral contracts before implementation details

`case.yaml` declares `expected_behavior`. Tests should primarily assert those outcomes. Static checks can enforce important structural constraints when behavior alone cannot distinguish a safe fix—for example, preventing a global lock from masquerading as a concurrency repair or requiring a stable idempotency key to reach a downstream gateway.

### Visible reproduction + withheld evaluator checks

The broken `repo/` contains enough visible information to reproduce the issue. Additional evaluators live in `tests_hidden/` and are not copied into the writable attempt workspace or included in provider prompts.

This separation tests generalization beyond the obvious visible assertion and makes test-tampering harder.

In the public GitHub repository, evaluator files are still readable by a human. This is deliberate for auditability. It is not equivalent to a private leaderboard holdout. A hosted competitive benchmark should maintain a second private pack and publish only aggregate outcomes.

## Manifest schema

Each case declares:

- stable `id` and descriptive title;
- stack labels;
- defect category;
- difficulty (`medium`, `hard`, `expert`);
- security impact where applicable;
- behavioral contract;
- sandbox image/resource policy;
- ordered check commands, stages, weights, and optional timeouts/images;
- changed-line budget;
- searchable tags.

Non-regression check weights must sum to 100. This is validated at manifest load time.

## Fixture layout

```text
benchmarks/<id>/
├── case.yaml
├── issue.md
├── mock.patch
├── repo/
│   ├── application/config/query files
│   └── tests/                 # public reproduction
└── tests_hidden/
    ├── grader.*               # evaluator-only behavioral checks
    └── optional analyzer config
```

The attempt workspace receives only `repo/` plus the submitted patch. Hidden checks are mounted read-only as `/grader` when each evaluator container starts.

## Difficulty

Difficulty is editorial metadata, not part of the numerical score.

- **medium**: one main defect with a clear reproduction, but still requires correct framework/tool behavior.
- **hard**: multiple plausible fixes exist and at least one obvious repair creates another bug or violates an invariant.
- **expert**: concurrency, replay, transactional, or similarly subtle behavior where a locally plausible patch is insufficient.

Difficulty should be calibrated with measured human/model results over time, not treated as permanent truth.

## Security implications

Security-relevant cases document concrete impact rather than attaching a generic security tag. Examples include cross-tenant billing disclosure, cross-tenant admin privilege, duplicate financial credit, and stale authorization-relevant state.

Security-stage checks receive explicit score weight so a patch that fixes a visible symptom but leaves the trust-boundary failure does not receive a near-perfect result.

## Baseline execution

Every evaluation first runs the declared checks against the broken fixture. This has three purposes:

1. prove that the fixture is actually broken;
2. record the original failure shown in the dashboard;
3. distinguish **new** regressions from checks that were already failing before the patch.

Benchmark maintainers should treat unexpectedly passing primary baseline checks as case-quality drift.

## Mutation-style checks

The benchmark uses targeted mutation/adversarial checks rather than requiring a heavyweight mutation framework for every stack. A mutation-stage evaluator should perturb the inputs or scenario in a way likely to defeat an overfit patch, for example:

- adversarial tenant IDs that defeat prefix matching;
- 30 concurrent same-key cache misses;
- multiple webhook replays after local persistence failures;
- a large customer list to expose remaining N+1 behavior;
- independent subscriptions/keys to reveal accidental global serialization.

A case can adopt a full mutation-testing engine when it adds signal without making the fixture disproportionately large.

## Code intelligence

Static tools are secondary deterministic signals, not replacements for behavioral tests.

Current integrations include:

- Ruff;
- mypy;
- Semgrep with case-specific rules;
- Tree-sitter parsing/structure inspection;
- TypeScript compiler;
- ESLint;
- `sqlglot` PostgreSQL parsing for SQL/config cases.

Case manifests decide which tools are relevant. The benchmark does not award points merely for running every tool on every language.

## Patch constraints

Before application, a patch is rejected if it:

- is empty;
- contains an absolute or parent-traversal path;
- targets `.git` or `.github`;
- targets a test path.

The patch is checked and applied inside a dedicated trusted Git image, not by executing a host-side fixture command.

These constraints intentionally narrow the benchmark to application repairs rather than test rewrites or evaluator attacks.

## Provider context

Agent providers receive:

- `issue.md`;
- the declared behavioral contract;
- a bounded text snapshot of visible repository files;
- an instruction to return only a unified diff and make the smallest correct change.

They do not receive `tests_hidden/` or `mock.patch` through the provider adapter.

The current provider interface is intentionally simple and comparable. It does not claim to replicate a full autonomous coding agent with shell/search iterations. A future agent protocol can add tool-use trajectories as a separate mode while retaining the same final deterministic evaluation.

## Dataset versioning

Benchmark cases are normal Git content. Every published comparison should include the repository commit SHA. Changing a case, hidden evaluator, scoring weight, Docker image definition, or provider prompt changes the experimental instrument and should be treated as a new benchmark revision.

## Case review checklist

Before merging a new case:

- broken baseline reproduces the stated defect;
- mock patch fixes the intended behavior;
- hidden tests are not copied into the attempt workspace;
- expected behavior does not reveal the exact patch unnecessarily;
- scoring totals 100 for non-regression stages;
- at least one regression invariant exists;
- security impact/check exists when appropriate;
- network is not required;
- tool/runtime dependencies exist in a trusted evaluator image;
- fixture has no symlinks;
- patch budget is reasonable;
- case remains understandable in isolation.
