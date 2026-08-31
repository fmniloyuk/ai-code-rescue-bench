# Contributing

Contributions are welcome, especially new realistic defect cases, stronger deterministic checks, sandbox hardening, and reproducibility improvements.

Before opening a pull request:

```bash
python -m pip install -e '.[dev]'
ruff check src tests tools
pytest
cd web && npm install && npm run build
```

For benchmark changes, also build the trusted evaluator images and run the affected case's deterministic mock proposal:

```bash
make images
rescuebench agent <case-id> --provider mock
```

New cases should follow the checklist in `docs/BENCHMARK_DESIGN.md`. Do not add fabricated model/human results. If you contribute measured results, include the benchmark SHA, provider/model identifiers, prompt revision, date, trial protocol, raw artifacts, and cost assumptions.

Security-sensitive changes should preserve the rule that benchmark-provided executable commands never run directly on the host.
