from rescuebench.models import CheckResult
from rescuebench.scoring import score_attempt


def result(stage: str, passed: bool, weight: float, name: str | None = None) -> CheckResult:
    return CheckResult(
        name=name or f"{stage}-check",
        stage=stage,  # type: ignore[arg-type]
        passed=passed,
        exit_code=0 if passed else 1,
        duration_ms=1,
        weight=weight,
    )


def test_score_is_deterministic_and_penalizes_real_regressions_and_large_diffs() -> None:
    checks = [
        result("hidden", True, 80),
        result("security", True, 20),
        result("regression", False, 0, "compat"),
    ]
    baseline = [result("regression", True, 0, "compat")]
    score = score_attempt(checks, changed_lines=40, budget=20, baseline_checks=baseline)
    assert score.raw_score == 100
    assert score.regression_penalty == 5
    assert score.changed_lines_penalty == 2
    assert score.final_score == 93


def test_preexisting_regression_failure_is_not_charged_again() -> None:
    checks = [result("hidden", True, 100), result("regression", False, 0, "existing")]
    baseline = [result("regression", False, 0, "existing")]
    score = score_attempt(checks, changed_lines=1, budget=10, baseline_checks=baseline)
    assert score.regression_count == 0
    assert score.final_score == 100
