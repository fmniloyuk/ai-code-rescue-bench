from __future__ import annotations

import json
import sys
from pathlib import Path


EXPECTED_CASES = set(sys.argv[1:])
if not EXPECTED_CASES:
    raise SystemExit("usage: assert-reference-results.py <case-id> [<case-id> ...]")

results: dict[str, dict[str, object]] = {}
for path in Path("artifacts/runs").glob("*/result.json"):
    data = json.loads(path.read_text(encoding="utf-8"))
    case_id = data.get("case_id")
    if isinstance(case_id, str) and case_id in EXPECTED_CASES:
        results[case_id] = data

missing = EXPECTED_CASES - results.keys()
if missing:
    raise SystemExit(f"missing reference results for: {', '.join(sorted(missing))}")

for case_id in sorted(EXPECTED_CASES):
    result = results[case_id]
    score = result["score"]
    if not isinstance(score, dict) or score.get("final_score") != 100.0:
        raise SystemExit(f"reference mock for {case_id} did not score 100: {score}")
    baseline = result.get("baseline_checks")
    if not isinstance(baseline, list) or not any(
        isinstance(check, dict) and check.get("passed") is False for check in baseline
    ):
        raise SystemExit(f"broken baseline for {case_id} has no failing check")
    checks = result.get("checks")
    if not isinstance(checks, list) or not checks or not all(
        isinstance(check, dict) and check.get("passed") is True for check in checks
    ):
        raise SystemExit(f"reference mock for {case_id} has a failing repaired check")
    print(f"{case_id}: reference mock=100, broken baseline confirmed")
