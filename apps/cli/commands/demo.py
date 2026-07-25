"""aegis demo — One-command demo experience."""
import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def demo(
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
    transactions: int = typer.Option(5000, "--transactions", "-t", help="Number of transactions to generate"),
):
    """Launch the full AegisOS demo — generates data, starts services, opens dashboard."""
    import subprocess
    import sys
    import time
    from pathlib import Path

    from apps.cli.output import console, print_banner

    print_banner()
    console.print("\n[header]Starting AegisOS Demo[/header]\n")

    # Step 1: Generate synthetic data
    console.print("[info]Step 1/4:[/info] Generating synthetic data...")

    from apps.cli.commands.generate import generate

    generate(
        users=500,
        transactions=transactions,
        fraud_rate=0.08,
        output="datasets/generated",
        seed=42,
    )

    # Step 2: Start infrastructure via docker-compose (if available)
    compose_file = Path("docker-compose.yml")
    if compose_file.exists():
        console.print("\n[info]Step 2/4:[/info] Starting infrastructure services...")
        try:
            subprocess.run(
                ["docker", "compose", "up", "-d", "redis", "postgres"],
                capture_output=True, timeout=60,
            )
            console.print("  [success]Redis + PostgreSQL started[/success]")
            time.sleep(2)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            console.print("  [warning]Docker not available — using in-memory backends[/warning]")
    else:
        console.print("\n[info]Step 2/4:[/info] [warning]No docker-compose.yml — using in-memory backends[/warning]")

    # Step 3: Start API server in background
    console.print("\n[info]Step 3/4:[/info] Starting AegisOS API server...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3)

    if api_process.poll() is not None:
        console.print("  [error]API server failed to start[/error]")
        raise typer.Exit(1)
    console.print("  [success]API running on http://localhost:8000[/success]")

    # Step 4: Open browser
    if not no_browser:
        console.print("\n[info]Step 4/4:[/info] Opening dashboard...")
        import webbrowser
        webbrowser.open("http://localhost:3000")
    else:
        console.print("\n[info]Step 4/4:[/info] Dashboard available at http://localhost:3000")

    console.print("\n[success]Demo is running![/success]")
    console.print("[dim]Press Ctrl+C to stop all services[/dim]\n")

    try:
        api_process.wait()
    except KeyboardInterrupt:
        console.print("\n[info]Shutting down...[/info]")
        api_process.terminate()
        api_process.wait(timeout=5)
        console.print("[success]Demo stopped.[/success]")
