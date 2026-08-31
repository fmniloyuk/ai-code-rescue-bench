# ADR 0004: Keep the dashboard read-only

- Status: Accepted
- Date: 2026-08-31

## Context

A dashboard improves auditability, but adding an HTTP endpoint that accepts patches or arbitrary benchmark commands would turn a local visualization service into a remote code-execution surface.

## Decision

The FastAPI service exposes only health, benchmark metadata, and persisted result reads. Evaluation is initiated from the CLI or controlled CI/worker processes. The React dashboard renders existing artifacts only.

## Consequences

- The UI can be safely reasoned about separately from the execution plane.
- A future hosted service must introduce an authenticated queue/worker boundary rather than calling the evaluator in a request handler.
- Local users run `rescuebench agent` / `rescuebench evaluate` first and then inspect results in the dashboard.
