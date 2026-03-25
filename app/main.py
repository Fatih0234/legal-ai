from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.schemas import CaseProfile

app = typer.Typer(help="Germany Café Navigator — regulatory checklist generator")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    json_file: Path = typer.Option(None, "--json", "-j", help="Path to case JSON file"),
    live: bool = typer.Option(
        False, "--live", help="Fetch live data from SDG portal (NRW)"
    ),
) -> None:
    """Evaluate a case and print the regulatory checklist."""
    if ctx.invoked_subcommand is not None:
        return
    if json_file is None:
        console.print("[red]Error:[/red] --json is required")
        raise typer.Exit(1)
    if not json_file.exists():
        console.print(f"[red]Error:[/red] File not found: {json_file}")
        raise typer.Exit(1)

    raw = json.loads(json_file.read_text())
    case_profile = CaseProfile.model_validate(raw)

    if live:
        from app.orchestrator import evaluate_case_live

        result = asyncio.run(evaluate_case_live(case_profile))
    else:
        from app.orchestrator import evaluate_case

        result = asyncio.run(evaluate_case(case_profile))

    # Print summary
    if result.summary:
        console.print(Panel(result.summary, title="Summary", border_style="green"))

    # Must do now
    if result.must_do_now:
        table = Table(title="Must Do Now", show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Action", style="bold")
        for i, item in enumerate(result.must_do_now, 1):
            table.add_row(str(i), item)
        console.print(table)

    # Conditional steps
    if result.conditional_steps:
        table = Table(
            title="Conditional Steps (depends on alcohol / premises / staff)",
            show_lines=True,
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Action", style="yellow")
        for i, item in enumerate(result.conditional_steps, 1):
            table.add_row(str(i), item)
        console.print(table)

    # Risk flags
    if result.risk_flags:
        for rf in result.risk_flags:
            style = {"info": "blue", "warning": "yellow", "critical": "red"}.get(
                rf.severity, "white"
            )
            console.print(
                f"  [{style}][{rf.severity.upper()}][/{style}] {rf.category}: {rf.description}"
            )
            if rf.recommendation:
                console.print(f"    → {rf.recommendation}")

    # Open questions
    if result.open_questions:
        console.print(
            Panel(
                "\n".join(f"• {q}" for q in result.open_questions),
                title="Open Questions",
                border_style="yellow",
            )
        )

    # Official links
    if result.official_links:
        console.print("\n[bold]Official Links:[/bold]")
        for link in result.official_links:
            console.print(f"  → {link}")

    # JSON output
    console.print("\n[dim]Full JSON output:[/dim]")
    console.print_json(result.model_dump_json(indent=2))


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
) -> None:
    """Start the web UI with form + chat."""
    import uvicorn

    console.print(f"[green]Starting web server at http://{host}:{port}[/green]")
    console.print(f"[dim]Open: http://{host}:{port}/[/dim]")
    uvicorn.run("app.web:app", host=host, port=port)


@app.command()
def chat() -> None:
    """Start interactive chat in the terminal."""
    from app.chat_agent import chat_agent as agent
    from app.agent import AppDeps
    import httpx

    async def run_chat():
        deps = AppDeps(http_client=httpx.AsyncClient())
        await agent.to_cli(deps=deps)

    asyncio.run(run_chat())


if __name__ == "__main__":
    app()
