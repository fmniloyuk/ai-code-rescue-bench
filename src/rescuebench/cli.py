from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .catalog import BenchmarkCatalog, find_repo_root
from .context import build_provider_context
from .evaluator import Evaluator
from .providers import get_provider

app = typer.Typer(no_args_is_help=True, help="Reproducible software repair benchmark runner")
console = Console()


def _catalog() -> tuple[Path, BenchmarkCatalog]:
    root = find_repo_root()
    return root, BenchmarkCatalog(root)


@app.command("list")
def list_cases() -> None:
    _, catalog = _catalog()
    table = Table("Case", "Difficulty", "Category", "Stack")
    for case in catalog.summaries():
        table.add_row(case.id, case.difficulty, case.defect_category, ", ".join(case.stack))
    console.print(table)


@app.command()
def evaluate(
    case_id: str,
    patch: Annotated[Path, typer.Option("--patch", exists=True, dir_okay=False)],
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    root, catalog = _catalog()
    manifest, case_dir = catalog.load(case_id)
    result = Evaluator(root).evaluate(
        manifest,
        case_dir,
        patch.read_text(encoding="utf-8"),
        mode="human",
    )
    if json_output:
        console.print_json(json.dumps(result.model_dump(mode="json")))
    else:
        console.print(f"[bold]{result.case_id}[/bold] score: {result.score.final_score:.2f}/100")
        console.print(f"artifact: {result.artifact_dir}")


@app.command()
def agent(
    case_id: str,
    provider: str = typer.Option("mock", "--provider"),
    model: str | None = typer.Option(None, "--model"),
    prompt_id: str = typer.Option("default", "--prompt-id"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    root, catalog = _catalog()
    manifest, case_dir = catalog.load(case_id)
    context = build_provider_context(manifest, case_dir, prompt_id=prompt_id)
    proposal = get_provider(provider).propose(context, model=model)
    result = Evaluator(root).evaluate(
        manifest,
        case_dir,
        proposal.patch,
        mode="agent",
        proposal=proposal,
    )
    if json_output:
        console.print_json(json.dumps(result.model_dump(mode="json")))
    else:
        console.print(f"[bold]{result.case_id}[/bold] score: {result.score.final_score:.2f}/100")
        console.print(f"provider: {result.provider} / {result.model}")
        console.print(f"artifact: {result.artifact_dir}")


@app.command()
def compare(limit: int = typer.Option(20, min=1, max=500)) -> None:
    root, _ = _catalog()
    results = Evaluator(root).store.list()[:limit]
    table = Table("Run", "Case", "Mode", "Provider", "Score", "Runtime ms", "Cost USD")
    for result in results:
        cost = result.usage.estimated_cost_usd if result.usage else None
        table.add_row(
            result.run_id,
            result.case_id,
            result.mode,
            result.provider or "human",
            f"{result.score.final_score:.2f}",
            str(result.runtime_ms),
            "n/a" if cost is None else f"{cost:.6f}",
        )
    console.print(table)


@app.command()
def doctor() -> None:
    completed = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise typer.Exit("Docker daemon is unavailable")
    console.print(f"Docker server: {completed.stdout.strip()}")
    console.print("Sandbox policy: network=none, cap-drop=ALL, no-new-privileges, pids/memory/cpu limits")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run("rescuebench.api:app", host=host, port=port, reload=False)
