# ADR 0003: Execute benchmark code only inside constrained Docker sandboxes

- Status: Accepted
- Date: 2026-08-31

## Context

Broken repositories and generated patches are executable untrusted input. Running their test/build commands on a developer or CI host would make the benchmark itself a code-execution vulnerability.

## Decision

The host runner never executes benchmark-provided commands directly. It invokes disposable Docker containers with networking disabled, resource/PID limits, read-only root filesystem, dropped capabilities, no-new-privileges, non-root identity, timeouts, and narrowly scoped mounts. Patch application also occurs in a trusted container.

## Consequences

- Local/CI evaluation has a meaningful containment boundary.
- Docker must be available to execute cases.
- Containers still share the host kernel, so a public hostile-submission service needs VM/microVM defense-in-depth.
- Candidate Docker infrastructure is parsed rather than blindly launched.
