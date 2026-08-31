from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Stage = Literal["build", "public", "hidden", "security", "quality", "mutation", "regression"]
Difficulty = Literal["medium", "hard", "expert"]


class SandboxSpec(BaseModel):
    image: str
    cpus: float = Field(default=1.0, gt=0, le=4)
    memory: str = "512m"
    pids: int = Field(default=128, ge=16, le=512)
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    network: Literal["none"] = "none"


class CheckSpec(BaseModel):
    name: str
    stage: Stage
    command: list[str]
    weight: float = Field(default=0, ge=0, le=100)
    image: str | None = None
    timeout_seconds: int | None = Field(default=None, ge=1, le=600)


class CaseManifest(BaseModel):
    id: str
    title: str
    stack: list[str]
    defect_category: str
    difficulty: Difficulty
    security_implications: str | None = None
    expected_behavior: list[str]
    sandbox: SandboxSpec
    checks: list[CheckSpec]
    changed_lines_budget: int = Field(default=20, ge=1)
    tags: list[str] = []

    @model_validator(mode="after")
    def validate_weights(self) -> "CaseManifest":
        weighted = sum(check.weight for check in self.checks if check.stage != "regression")
        if abs(weighted - 100.0) > 0.001:
            raise ValueError(f"non-regression check weights must total 100, got {weighted}")
        return self


class ProviderUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None


class PatchProposal(BaseModel):
    provider: str
    model: str
    patch: str
    prompt_id: str = "default"
    usage: ProviderUsage = ProviderUsage()
    latency_ms: int | None = None


class CheckResult(BaseModel):
    name: str
    stage: Stage
    passed: bool
    exit_code: int
    duration_ms: int
    stdout: str = ""
    stderr: str = ""
    weight: float
    timed_out: bool = False


class ScoreCard(BaseModel):
    raw_score: float
    changed_lines_penalty: float
    regression_penalty: float
    final_score: float
    changed_lines: int
    regression_count: int
    stage_scores: dict[str, float]


class EvaluationResult(BaseModel):
    run_id: str
    case_id: str
    mode: Literal["human", "agent"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str | None = None
    model: str | None = None
    prompt_id: str | None = None
    usage: ProviderUsage | None = None
    patch: str
    baseline_checks: list[CheckResult]
    checks: list[CheckResult]
    score: ScoreCard
    runtime_ms: int
    artifact_dir: str


class CaseSummary(BaseModel):
    id: str
    title: str
    stack: list[str]
    defect_category: str
    difficulty: Difficulty
    security_implications: str | None
    path: Path
