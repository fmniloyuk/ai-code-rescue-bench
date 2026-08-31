# ADR 0002: Deterministic validation is the primary judge

- Status: Accepted
- Date: 2026-08-31

## Context

LLM-as-judge systems are attractive for flexible code review but introduce model variance, cost, prompt sensitivity, and self-preference. Most software-repair claims can instead be tested with executable behavior and static invariants.

## Decision

LLMs may generate candidate patches but do not determine the benchmark's primary correctness score. Cases use deterministic build, public, hidden, security, quality, mutation, and regression checks.

## Consequences

- Scores are auditable down to individual commands.
- The benchmark can run fully offline with deterministic mock proposals.
- Maintainers must invest in strong tests instead of delegating ambiguous validation to another model.
- Subjective signals, if added later, must be reported separately from deterministic correctness.
