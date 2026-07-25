"""Rich console output utilities for the AegisOS CLI."""
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

aegis_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "header": "bold magenta",
    "score.low": "green",
    "score.medium": "yellow",
    "score.high": "red",
    "score.critical": "bold red on white",
})

console = Console(theme=aegis_theme)


def print_banner():
    banner = Text()
    banner.append("AEGIS", style="bold cyan")
    banner.append("OS", style="bold white")
    banner.append(" v0.1.0", style="dim")
    console.print(Panel(
        banner,
        subtitle="Autonomous AI Operating System for Financial Intelligence",
        border_style="cyan",
    ))


def print_score_result(result: dict):
    score = result.get("risk_score", 0.0)
    level = result.get("risk_level", "unknown")

    if score < 0.3:
        style = "score.low"
    elif score < 0.6:
        style = "score.medium"
    elif score < 0.85:
        style = "score.high"
    else:
        style = "score.critical"

    table = Table(title="Transaction Risk Assessment", border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Transaction ID", result.get("transaction_id", "N/A"))
    table.add_row("Risk Score", Text(f"{score:.4f}", style=style))
    table.add_row("Risk Level", Text(level.upper(), style=style))
    table.add_row("Verdict", result.get("verdict", "N/A"))

    reasons = result.get("reasons", [])
    if reasons:
        table.add_row("Reasons", "\n".join(f"- {r}" for r in reasons))

    console.print(table)


def print_status_table(services: list[dict]):
    table = Table(title="AegisOS System Status", border_style="cyan")
    table.add_column("Service", style="bold")
    table.add_column("Status")
    table.add_column("Latency")

    for svc in services:
        status_style = "success" if svc["healthy"] else "error"
        status_text = "UP" if svc["healthy"] else "DOWN"
        table.add_row(
            svc["name"],
            Text(status_text, style=status_style),
            f"{svc.get('latency_ms', 0):.0f}ms",
        )

    console.print(table)


def get_progress():
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    )
