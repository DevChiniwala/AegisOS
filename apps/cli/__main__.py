"""
AegisOS CLI entry point.

Usage:
    aegis serve         Start the API server
    aegis score         Score a transaction for fraud risk
    aegis investigate   Run a multi-agent investigation
    aegis generate      Generate synthetic transaction data
    aegis demo          One-command demo experience
    aegis status        Check system health
"""
import typer

from apps.cli.commands.demo import app as demo_app
from apps.cli.commands.generate import app as generate_app
from apps.cli.commands.investigate import app as investigate_app
from apps.cli.commands.score import app as score_app
from apps.cli.commands.serve import app as serve_app
from apps.cli.commands.status import app as status_app

app = typer.Typer(
    name="aegis",
    help="AegisOS — The Autonomous AI Operating System for Financial Intelligence",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

app.add_typer(serve_app, name="serve", help="Start the AegisOS API server")
app.add_typer(score_app, name="score", help="Score transactions for fraud risk")
app.add_typer(investigate_app, name="investigate", help="Run multi-agent investigations")
app.add_typer(generate_app, name="generate", help="Generate synthetic data")
app.add_typer(demo_app, name="demo", help="One-command demo experience")
app.add_typer(status_app, name="status", help="Check system health")


def main():
    app()


if __name__ == "__main__":
    main()
