from __future__ import annotations

from collections import defaultdict

from .models import CheckResult, ScoreCard


def score_attempt(checks: list[CheckResult], changed_lines: int, budget: int) -> ScoreCard:
    raw = sum(result.weight for result in checks if result.stage != "regression" and result.passed)
    regression_count = sum(1 for result in checks if result.stage == "regression" and not result.passed)
    regression_penalty = min(25.0, regression_count * 5.0)
    changed_penalty = min(5.0, max(0, changed_lines - budget) * 0.1)
    stage_scores: dict[str, float] = defaultdict(float)
    for result in checks:
        if result.stage != "regression" and result.passed:
            stage_scores[result.stage] += result.weight
    final = max(0.0, min(100.0, raw - regression_penalty - changed_penalty))
    return ScoreCard(
        raw_score=round(raw, 2),
        changed_lines_penalty=round(changed_penalty, 2),
        regression_penalty=round(regression_penalty, 2),
        final_score=round(final, 2),
        changed_lines=changed_lines,
        regression_count=regression_count,
        stage_scores=dict(stage_scores),
    )
