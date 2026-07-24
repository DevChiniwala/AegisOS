"""aegis score — Score transactions for fraud risk."""
import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def score(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file with transaction data"),
    amount: Optional[float] = typer.Option(None, "--amount", "-a", help="Transaction amount"),
    sender: Optional[str] = typer.Option(None, "--sender", "-s", help="Sender ID"),
    receiver: Optional[str] = typer.Option(None, "--receiver", "-r", help="Receiver ID"),
    channel: str = typer.Option("online", "--channel", "-c", help="Transaction channel"),
    currency: str = typer.Option("USD", "--currency", help="Transaction currency"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AegisOS API URL"),
):
    """Score a transaction for fraud risk."""
    from apps.cli.output import console, print_score_result

    if file:
        data = json.loads(file.read_text())
    elif amount is not None:
        data = {
            "transaction_id": str(uuid4()),
            "amount": amount,
            "currency": currency,
            "sender_id": sender or "user_unknown",
            "receiver_id": receiver or "merchant_unknown",
            "channel": channel,
            "timestamp": None,
        }
    else:
        console.print("[error]Provide --file or --amount[/error]")
        raise typer.Exit(1)

    import httpx

    with console.status("[info]Scoring transaction...[/info]"):
        try:
            resp = httpx.post(f"{api_url}/api/v1/transactions/score", json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except httpx.ConnectError:
            console.print("[error]Cannot connect to AegisOS API. Is it running? (aegis serve)[/error]")
            raise typer.Exit(1)
        except httpx.HTTPStatusError as e:
            console.print(f"[error]API error: {e.response.status_code} — {e.response.text}[/error]")
            raise typer.Exit(1)

    print_score_result(result)
