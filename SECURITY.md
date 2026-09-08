# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub's security reporting features for this repository when available. Do not open a public issue containing an active sandbox escape or credential-exposure proof of concept before maintainers have had a reasonable opportunity to respond.

Include the affected commit, environment, reproduction steps, impact, and any suggested mitigation.

## Scope

Security-sensitive areas include:

- Docker sandbox argument construction;
- filesystem/path traversal and symlink handling;
- patch application;
- hidden evaluator isolation;
- result redaction;
- provider credential handling;
- API endpoints that could reach evaluation code;
- evaluator/patcher image supply chain.

## Deployment warning

The included sandbox is designed for local/CI benchmark execution. Do not expose it as an internet-facing arbitrary-code execution service without the additional VM/microVM, daemon, network, quota, image-verification, authentication, and abuse controls described in `docs/SANDBOX_SECURITY.md`.
