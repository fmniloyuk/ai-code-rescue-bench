from rescuebench.models import CheckResult
from rescuebench.scoring import score_attempt


def result(stage: str, passed: bool, weight: float) -> CheckResult:
    return CheckResult(
        name=f"{stage}-check",
        stage=stage,  # type: ignore[arg-type]
        passed=passed,
        exit_code=0 if passed else 1,
        duration_ms=1,
        weight=weight,
    )


def test_score_is_deterministic_and_penalizes_regressions_and_large_diffs() -> None:
    checks = [result("hidden", True, 80), result("security", True, 20), result("regression", False, 0)]
    score = score_attempt(checks, changed_lines=40, budget=20)
    assert score.raw_score == 100
    assert score.regression_penalty == 5
    assert score.changed_lines_penalty == 2
    assert score.final_score == 93
