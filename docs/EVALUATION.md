# Evaluation Methodology

## Evaluation unit

An attempt is the tuple:

```text
benchmark revision
case id
mode (human | agent)
provider/model (if agent)
prompt id
trial
submitted unified diff
```

The output is an immutable-style JSON result artifact plus the normalized patch.

## Pipeline

1. Load and validate `case.yaml`.
2. Copy only the broken `repo/` into a fresh temporary workspace; reject symlinks.
3. Run all declared checks on the broken baseline inside sandboxes.
4. Normalize and validate patch paths.
5. `git apply --check` and apply inside the trusted patcher sandbox.
6. Run the same declared checks against the repaired workspace.
7. Calculate deterministic weighted score and penalties.
8. Persist `result.json` and `attempt.patch`.
9. Delete the temporary workspace.

The baseline and repaired executions use the same case manifest and sandbox policy.

## Stages

### Build

Compilation, syntax, or type-level viability that must hold before deeper behavior is trusted.

Examples: `compileall`, `tsc --noEmit`, SQL/YAML parse.

### Public

The visible issue reproduction. Passing this is necessary but deliberately insufficient for a high score.

### Hidden

Additional behavioral contracts not included in the provider/attempt workspace. These commonly test alternate inputs, failure paths, ordering, or concurrency.

### Security

Trust-boundary invariants such as exact tenant equality, stable webhook idempotency, or avoiding unsafe host-network workarounds.

### Quality

Deterministic static/code-intelligence signals relevant to the case: Ruff, mypy, Semgrep, Tree-sitter, ESLint, TypeScript compiler, SQL parsing.

### Mutation

Adversarial or stress variants designed to catch overfitting to the visible example.

### Regression

Behavior expected to work before and after the repair. Regression checks carry zero positive weight and instead contribute a penalty only when a check that passed on the baseline becomes failing after the patch.

## Score

Each case's non-regression check weights sum to exactly 100.

```text
raw_score = sum(weight for passing check if stage != regression)

changed_lines_penalty = min(
    5,
    max(0, changed_lines - changed_lines_budget) * 0.1
)

regression_count = count(
    patched regression check fails
    AND corresponding baseline regression check passed or did not exist
)

regression_penalty = min(25, regression_count * 5)

final_score = clamp(
    raw_score - changed_lines_penalty - regression_penalty,
    0,
    100
)
```

Changed lines count additions and deletions in the normalized unified diff, excluding diff headers and hunk headers.

The changed-line penalty is intentionally small. It discourages replacing an entire fixture to solve a localized issue but should not dominate correctness.

## Why no LLM correctness judge?

When a deterministic test, analyzer, or invariant can decide correctness, an LLM judge adds avoidable variance, prompt sensitivity, model drift, cost, and potential self-preference bias.

The benchmark therefore uses LLMs on the **candidate generation** side only.

A future subjective signal should be:

- separately named;
- non-authoritative by default;
- versioned with exact model/prompt;
- reported separately from deterministic correctness;
- never used to conceal the absence of executable validation.

## Static analysis is not the main judge either

A Semgrep match disappearing does not prove the bug is fixed. A linter passing does not prove authorization. Static checks receive bounded weight and sit alongside stronger behavioral/security checks.

## Mutation testing

Mutation-style checks are case-specific because the most useful mutation for a concurrency bug differs from one for SQL authorization or React cleanup.

The benchmark supports a `mutation` stage; maintainers can invoke a full mutation framework in that stage when useful. Current fixtures prefer focused adversarial variants to keep each case understandable and deterministic.

## Model/provider metadata

Agent runs preserve:

- provider adapter;
- model string;
- prompt id;
- input/output tokens when the provider reports them;
- estimated cost only when explicit per-million-token rates are supplied to the runner;
- generation latency in the proposal model where available.

Prices are not embedded as timeless constants. A result with no configured pricing stores `estimated_cost_usd = null`.

## Prompt comparisons

`prompt_id` is part of each run artifact and dashboard grouping. For a publishable experiment, store the actual prompt template alongside the benchmark revision or reference an immutable prompt file/commit; a label by itself is not sufficient provenance.

## Human baseline

Human attempts use the same patch path, sandbox, checks, score, and artifact schema. A serious human baseline should define:

- participant experience level;
- whether documentation/search/tools are allowed;
- time budget;
- whether hidden benchmark source is inaccessible;
- compensation/incentives;
- number of participants/cases;
- treatment of incomplete attempts.

Comparing an unconstrained expert human who has seen the hidden tests with a time-limited model run is not meaningful.

## Repeated trials

For stochastic model providers, run multiple independent attempts per case/prompt/model. Preserve every raw artifact rather than only the best run.

Useful summaries include:

- mean/median final score;
- standard deviation or interquartile range;
- min/max for small exploratory sets;
- pass rate above a predeclared threshold;
- pass@k only when `k` and the sampling protocol are clearly defined;
- mean tokens, latency, and cost.

The dashboard currently shows trial count, mean, and observed range as a compact exploratory view. Do not mistake this for inferential statistics.

## Statistical limitations

### Small, curated case set

Sixteen heterogeneous cases do not represent the full distribution of software engineering. Confidence intervals over these cases can falsely imply population generality if the case selection is not itself random.

### Cases are not IID

Multiple cases share languages, patterns, and evaluator infrastructure. Treating them as independent identically distributed draws understates uncertainty.

### Provider nondeterminism

Temperature zero does not guarantee identical model execution. Providers can change serving stacks, hidden system prompts, safety layers, routing, quantization, or model aliases without changing your benchmark code.

### Model/version drift

Record exact version identifiers where the provider exposes them and the experiment date. A marketing alias is weak provenance.

### Prompt sensitivity

A prompt is part of the treatment. Comparing models with materially different scaffolding can measure orchestration quality rather than model capability. That can be valid, but it must be named correctly.

### Public benchmark contamination

Once cases and reference mock patches are public, a future model may have encountered them during training or retrieval. The public set is valuable for reproducibility and engineering transparency but weakens claims of unseen generalization.

Use a private rotating holdout for competitive capability claims.

### Human selection effects

Human baselines are highly sensitive to expertise, motivation, time budget, tooling, and familiarity with the benchmark. Report those details.

### Multiple comparisons

Trying many prompt/model combinations and publishing only the best exaggerates performance. Predeclare the comparison or publish the full trial matrix.

### Cost comparisons

Token price alone omits retries, cache discounts, tool calls, latency, engineering overhead, and provider pricing changes. Preserve the rate assumptions used at evaluation time.

### Hidden test incompleteness

Passing every deterministic check proves conformity to the encoded contracts, not universal correctness. Tests can be incomplete. Benchmark maintainers should add regressions when a reasonable but incorrect patch earns an unexpectedly high score.

## Reporting checklist

A credible benchmark report should include:

- benchmark Git commit SHA;
- evaluator image digests where available;
- case list;
- provider and exact model ids;
- experiment dates;
- prompt/template revision;
- trial count and sampling parameters;
- human baseline protocol if used;
- complete raw run artifacts;
- aggregate statistic definition;
- token/cost rate assumptions;
- environment/runtime version;
- known failures or excluded cases;
- whether participants could inspect public hidden tests.

Do not fabricate missing results. `null`, `not measured`, and `not available` are valid benchmark data.
