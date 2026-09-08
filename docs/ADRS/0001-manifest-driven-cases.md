# ADR 0001: Manifest-driven benchmark cases

- Status: Accepted
- Date: 2026-08-31

## Context

A benchmark needs heterogeneous languages and defect types without turning the runner into a large switch statement keyed by case id.

## Decision

Each case owns a validated `case.yaml` declaring metadata, sandbox resources, commands, stages, weights, and changed-line budget. The runner is generic over that manifest.

## Consequences

- New cases can be added without editing evaluator control flow.
- The scoring contract is version-controlled beside the fixture.
- A malicious manifest remains untrusted command input, so every declared command must still execute inside the sandbox.
- Schema evolution must preserve or explicitly migrate benchmark reproducibility.
