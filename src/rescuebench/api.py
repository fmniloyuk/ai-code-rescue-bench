from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .artifacts import ArtifactStore
from .catalog import BenchmarkCatalog

ROOT = Path(__file__).resolve().parents[2]
CATALOG = BenchmarkCatalog(ROOT)
STORE = ArtifactStore(ROOT / "artifacts" / "runs")

app = FastAPI(title="AI Code Rescue Bench API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/cases")
def cases() -> list[dict[str, object]]:
    return [summary.model_dump(mode="json") for summary in CATALOG.summaries()]


@app.get("/api/runs")
def runs() -> list[dict[str, object]]:
    return [result.model_dump(mode="json") for result in STORE.list()]


@app.get("/api/runs/{run_id}")
def run(run_id: str) -> dict[str, object]:
    try:
        return STORE.get(run_id).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc
