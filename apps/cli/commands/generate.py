"""aegis generate — Generate synthetic transaction data."""
import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def generate(
    users: int = typer.Option(100, "--users", "-u", help="Number of users to generate"),
    transactions: int = typer.Option(1000, "--transactions", "-t", help="Number of transactions"),
    fraud_rate: float = typer.Option(0.05, "--fraud-rate", help="Fraction of fraudulent transactions"),
    output: str = typer.Option("datasets/generated", "--output", "-o", help="Output directory"),
    seed: int = typer.Option(42, "--seed", help="Random seed for reproducibility"),
):
    """Generate synthetic transaction data for testing."""
    from apps.cli.output import console, get_progress

    console.print(f"[header]Generating synthetic data[/header]")
    console.print(f"  Users: {users} | Transactions: {transactions} | Fraud rate: {fraud_rate:.1%}\n")

    import json
    import random
    from pathlib import Path
    from uuid import uuid4
    from datetime import datetime, timedelta

    random.seed(seed)
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    user_ids = [f"user_{i:04d}" for i in range(users)]
    merchant_ids = [f"merchant_{i:03d}" for i in range(users // 5)]
    channels = ["online", "mobile", "pos", "atm", "wire"]
    currencies = ["USD", "EUR", "GBP", "JPY"]

    generated_txs = []
    fraud_count = int(transactions * fraud_rate)

    with get_progress() as progress:
        task = progress.add_task("Generating transactions...", total=transactions)

        for i in range(transactions):
            is_fraud = i < fraud_count
            tx = {
                "transaction_id": str(uuid4()),
                "sender_id": random.choice(user_ids),
                "receiver_id": random.choice(merchant_ids),
                "amount": _generate_amount(is_fraud),
                "currency": random.choice(currencies),
                "channel": random.choice(channels),
                "timestamp": (datetime(2024, 1, 1) + timedelta(seconds=random.randint(0, 86400 * 365))).isoformat(),
                "is_fraud": is_fraud,
            }

            if is_fraud:
                tx["fraud_type"] = random.choice([
                    "account_takeover", "synthetic_identity", "card_not_present",
                    "money_laundering", "first_party_fraud",
                ])

            generated_txs.append(tx)
            progress.update(task, advance=1)

    random.shuffle(generated_txs)
    output_file = output_dir / "transactions.json"
    output_file.write_text(json.dumps(generated_txs, indent=2))

    console.print(f"\n[success]Generated {transactions} transactions ({fraud_count} fraudulent)[/success]")
    console.print(f"[info]Output: {output_file}[/info]")


def _generate_amount(is_fraud: bool) -> float:
    import random

    if is_fraud:
        patterns = [
            lambda: random.uniform(5000, 50000),
            lambda: random.uniform(9000, 9999),
            lambda: random.uniform(100, 500),
        ]
        return round(random.choice(patterns)(), 2)
    else:
        return round(random.uniform(5, 2000), 2)
