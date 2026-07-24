"""aegis serve — Start the AegisOS API server."""
import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development"),
    workers: int = typer.Option(1, help="Number of worker processes"),
):
    """Start the AegisOS API server."""
    import uvicorn
    from apps.cli.output import console, print_banner

    print_banner()
    console.print(f"[info]Starting AegisOS API on {host}:{port}...[/info]")

    uvicorn.run(
        "apps.api.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info",
    )
