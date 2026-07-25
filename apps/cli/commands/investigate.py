"""aegis investigate — Run multi-agent fraud investigations."""
import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def investigate(
    transaction_id: str = typer.Argument(..., help="Transaction ID to investigate"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AegisOS API URL"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream agent reasoning in real-time"),
):
    """Run a multi-agent investigation on a transaction."""
    import httpx

    from apps.cli.output import console

    console.print(f"[header]Investigating transaction: {transaction_id}[/header]\n")

    if stream:
        try:
            with httpx.stream(
                "POST",
                f"{api_url}/api/v1/investigations/stream",
                json={"transaction_id": transaction_id},
                timeout=120,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    _print_agent_event(line)
        except httpx.ConnectError:
            console.print("[error]Cannot connect to AegisOS API. Is it running? (aegis serve)[/error]")
            raise typer.Exit(1)
    else:
        with console.status("[info]Running investigation (this may take a moment)...[/info]"):
            try:
                resp = httpx.post(
                    f"{api_url}/api/v1/investigations/",
                    json={"transaction_id": transaction_id},
                    timeout=120,
                )
                resp.raise_for_status()
                result = resp.json()
            except httpx.ConnectError:
                console.print("[error]Cannot connect to AegisOS API.[/error]")
                raise typer.Exit(1)
            except httpx.HTTPStatusError as e:
                console.print(f"[error]API error: {e.response.status_code}[/error]")
                raise typer.Exit(1)

        _print_investigation_result(result)


def _print_agent_event(line: str):
    import json

    from apps.cli.output import console

    try:
        event = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        return

    agent = event.get("agent", "system")
    msg = event.get("message", "")
    event_type = event.get("type", "info")

    if event_type == "agent_start":
        console.print(f"  [cyan]{agent}[/cyan] started")
    elif event_type == "agent_complete":
        console.print(f"  [green]{agent}[/green] complete")
    elif event_type == "finding":
        console.print(f"  [yellow]{agent}[/yellow]: {msg}")
    else:
        console.print(f"  [dim]{agent}[/dim]: {msg}")


def _print_investigation_result(result: dict):
    from rich.panel import Panel

    from apps.cli.output import console

    verdict = result.get("verdict", "unknown")
    confidence = result.get("confidence", 0.0)
    summary = result.get("summary", "No summary available.")

    style = "green" if verdict == "legitimate" else "red"

    console.print(Panel(
        f"[bold]Verdict:[/bold] [{style}]{verdict.upper()}[/{style}]\n"
        f"[bold]Confidence:[/bold] {confidence:.1%}\n\n"
        f"{summary}",
        title="Investigation Complete",
        border_style="cyan",
    ))
