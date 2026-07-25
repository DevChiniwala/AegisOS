"""aegis status — Check system health."""
import time

import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def status(
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AegisOS API URL"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed status"),
):
    """Check the health of all AegisOS services."""
    import httpx

    from apps.cli.output import console, print_status_table

    services = []

    # Check API
    api_status = _check_service("AegisOS API", f"{api_url}/health")
    services.append(api_status)

    if api_status["healthy"] and verbose:
        try:
            resp = httpx.get(f"{api_url}/api/v1/dashboard/metrics", timeout=5)
            if resp.status_code == 200:
                metrics = resp.json()
                services.append({
                    "name": "Risk Engine",
                    "healthy": True,
                    "latency_ms": metrics.get("avg_scoring_latency_ms", 0),
                })
        except Exception:
            pass

    # Check Redis
    services.append(_check_redis())

    # Check PostgreSQL
    services.append(_check_postgres())

    print_status_table(services)

    all_healthy = all(s["healthy"] for s in services)
    if all_healthy:
        console.print("\n[success]All systems operational[/success]")
    else:
        down = [s["name"] for s in services if not s["healthy"]]
        console.print(f"\n[warning]Services down: {', '.join(down)}[/warning]")
        raise typer.Exit(1)


def _check_service(name: str, url: str) -> dict:
    import httpx

    start = time.perf_counter()
    try:
        resp = httpx.get(url, timeout=5)
        latency = (time.perf_counter() - start) * 1000
        return {"name": name, "healthy": resp.status_code == 200, "latency_ms": latency}
    except Exception:
        return {"name": name, "healthy": False, "latency_ms": 0}


def _check_redis() -> dict:
    try:
        import redis as redis_lib
        start = time.perf_counter()
        r = redis_lib.Redis(host="localhost", port=6379, socket_timeout=2)
        r.ping()
        latency = (time.perf_counter() - start) * 1000
        return {"name": "Redis", "healthy": True, "latency_ms": latency}
    except Exception:
        return {"name": "Redis", "healthy": False, "latency_ms": 0}


def _check_postgres() -> dict:
    try:
        import psycopg2
        start = time.perf_counter()
        conn = psycopg2.connect(
            host="localhost", port=5432,
            dbname="aegis", user="aegis", password="aegis",
            connect_timeout=2,
        )
        conn.close()
        latency = (time.perf_counter() - start) * 1000
        return {"name": "PostgreSQL", "healthy": True, "latency_ms": latency}
    except Exception:
        return {"name": "PostgreSQL", "healthy": False, "latency_ms": 0}
