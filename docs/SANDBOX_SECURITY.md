# Sandbox Security

## Threat model

Assume all of the following are hostile:

- source files in a benchmark fixture;
- test/build scripts inside the fixture;
- package/application code imported by those tests;
- submitted patch contents;
- filenames and repository layout;
- output written to stdout/stderr;
- code produced by an LLM provider.

Do **not** assume a benchmark repository is safe because it came from Git or because its declared defect looks ordinary.

The trusted computing base includes the host runner, Docker daemon/runtime, Linux kernel, evaluator image definitions, `rescuebench` orchestration code, and evaluator-only test pack.

## Core rule

> Benchmark-provided executable commands are never run directly on the host.

The host may perform non-executing file operations, validate patch text, create temporary directories, call the Docker CLI, and persist results. All declared case commands execute inside a constrained container.

Patch application itself runs in a dedicated trusted `rescuebench/patcher:local` image.

## Container policy

`DockerSandbox` applies these controls to every check:

- `--rm`: disposable container;
- `--init`: reap descendants;
- `--network none`: no network namespace connectivity;
- `--cpus`: CPU quota;
- `--memory`: hard memory limit;
- `--pids-limit`: fork/process limit;
- `--read-only`: immutable container root filesystem;
- `--cap-drop ALL`: no ambient Linux capabilities;
- `--security-opt no-new-privileges:true`;
- non-root UID/GID;
- small writable `/tmp` and `/run` tmpfs mounts with `noexec,nosuid,nodev`;
- wall-clock timeout enforced by the host orchestrator;
- bounded captured stdout/stderr.

The copied attempt workspace is the only writable bind mount required for normal evaluation. Evaluator-only files are mounted separately at `/grader` read-only.

## What is deliberately not mounted

Evaluator containers do not receive:

- `/var/run/docker.sock`;
- the host home directory;
- SSH credentials;
- cloud credentials;
- provider API keys;
- the benchmark repository root;
- arbitrary host paths;
- a writable hidden-evaluator directory.

Provider API calls occur before local patch evaluation and their secrets are never forwarded as evaluator environment variables.

## Filesystem defenses

The workspace builder rejects symlinks in the broken fixture before copying it. This prevents a fixture from smuggling a link to an unexpected host location into a bind-mounted tree.

Patch validation rejects:

- absolute paths;
- `..` traversal;
- `.git` and `.github` control paths;
- test paths.

`git apply --check` is performed before the actual apply, and both operations happen in the constrained patcher container.

## Hidden evaluator isolation

`tests_hidden/` is never copied into `/workspace`. It is mounted as `/grader:ro` only during check execution.

This prevents a normal candidate patch from directly editing evaluator files and prevents the provider context builder from accidentally including them.

It does **not** make hidden tests cryptographically secret in the public repository. See `BENCHMARK_DESIGN.md` for the distinction between auditability and a private leaderboard holdout.

## Network policy

Network access is disabled by default and the manifest schema currently permits only `network: none`.

This matters for both containment and reproducibility:

- untrusted code cannot exfiltrate data over ordinary container networking;
- tests cannot silently depend on live APIs;
- package installs cannot occur during a benchmark attempt;
- DNS/network variability does not change the result.

All needed dependencies must be baked into a trusted evaluator image before an attempt begins.

## Docker/configuration cases

A benchmark about Docker must not become an excuse to execute candidate infrastructure with elevated privileges.

Docker Compose and SQL/config fixtures are inspected with trusted parsers and deterministic semantic checks inside evaluator containers. The benchmark does not build an arbitrary fixture Dockerfile, start a candidate Compose stack, mount the Docker socket into a case, or grant privileged mode.

## Output handling

Stdout/stderr is capped before it is persisted so an attempt cannot trivially exhaust artifact storage with unlimited output.

Outputs from `hidden`, `security`, `mutation`, and `regression` stages are redacted in `EvaluationResult`; only status, exit code, runtime, timeout state, and score weight are surfaced. This reduces oracle leakage from evaluator internals.

## Timeouts and denial of service

Wall-clock timeout is enforced by the host-side Docker process call. Memory, CPU, and PID controls limit common resource-exhaustion attacks inside the container.

These controls reduce risk but do not eliminate every denial-of-service vector against the Docker daemon or shared kernel.

## Docker is not a perfect hostile sandbox

Docker containers share the host kernel. A kernel/runtime vulnerability can cross the isolation boundary. The local runner is therefore appropriate for curated benchmark fixtures and development, but it should not be exposed directly as a public arbitrary-code execution service.

For internet-facing third-party submissions, add another boundary:

1. enqueue only immutable case id + patch artifact;
2. start a disposable VM or microVM per job/worker batch;
3. run rootless Docker, gVisor, Kata Containers, Firecracker, or equivalent defense-in-depth inside that worker where practical;
4. use a dedicated kernel/runtime patched independently of developer machines;
5. block metadata-service and control-plane access at the VM network layer;
6. expose no long-lived secrets to the worker;
7. destroy the worker after evaluation;
8. publish only sanitized artifacts.

A production service should also define seccomp/AppArmor/SELinux policy, image signing/verification, registry allowlists, disk quotas, daemon isolation, rate limits, abuse monitoring, and emergency kill controls.

## Reproducibility and image trust

Evaluator package versions are pinned in Dockerfiles. Base image tags are intentionally human-readable in this portfolio implementation, which means upstream tag mutation remains a reproducibility limitation.

For a formal benchmark release, resolve every base/evaluator image to an immutable digest, record those digests with the benchmark Git revision, sign resulting evaluator images, and verify signatures/digests on workers before execution.

## Security properties this project does not claim

The project does not claim:

- VM-grade isolation from a hostile kernel exploit;
- cryptographic secrecy of public hidden tests;
- safe execution of arbitrary third-party Dockerfiles;
- supply-chain safety for images whose digests have not been locked;
- perfect resistance to side channels;
- safe multi-tenant public hosting with only the included local Docker policy.

These limitations are explicit because benchmark security is part of the engineering problem, not a footnote.
