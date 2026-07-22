# AegisOS

> "The Autonomous AI Operating System for Financial Intelligence."

AegisOS is the world's most advanced open-source fraud intelligence platform. Built for enterprise scale, it moves beyond simple classification to provide a comprehensive, multi-agent AI system capable of autonomous fraud detection, investigation, reasoning, and reporting.

## Overview

AegisOS is designed to detect and investigate a wide range of financial crimes including Credit Card Fraud, UPI Fraud, Wire Transfer Fraud, AML, Account Takeovers, and Synthetic Identities.

Unlike traditional systems that rely on static thresholds or a single ML classifier, AegisOS employs a **Modular Intelligence Architecture**:

*   **Tiered Scoring Engine**: Sub-20ms Fast-Path rules evaluation paired with SHAP-guided dynamic ensemble models.
*   **Graph Intelligence**: Deep entity resolution, heterophily-aware fraud ring detection, and money flow tracing.
*   **Behavioral AI**: Continual learning of user habits (spending, temporal, geographic, device) via temporal sequence modeling.
*   **Multi-Agent Investigation**: An orchestration of specialized AI agents (Transaction Investigator, Graph Detective, Behavior Analyst, Compliance Officer, etc.) that autonomously investigate flagged transactions and generate audit-ready Suspicious Activity Reports (SARs).
*   **Explainable AI (XAI)**: Every decision includes confidence scores, SHAP feature attributions, counterfactual reasoning, and natural language narratives.

## Architecture

AegisOS is built as a set of event-driven microservices.

```
API Gateway -> Event Bus (Kafka/Redis) -> Streaming Processor -> Feature Engine -> Risk Engine
```

For high-risk transactions, the `Risk Engine` triggers the `Multi-Agent Investigation` layer, which interacts with the `Graph Engine`, `Behavioral AI`, and `Memory Engine` to compile evidence.

### Tech Stack
*   **Core Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0
*   **ML & AI**: XGBoost, LightGBM, CatBoost, PyTorch (GraphSAGE, GAT, TGN)
*   **Databases**: PostgreSQL (Relational), Neo4j (Graph), Redis (Cache/Streams), Qdrant (Vector/Memory), MinIO (Object Storage)
*   **Frontend**: Next.js, React, TailwindCSS, shadcn/ui, React Flow

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.11+
*   `uv` or `pip`

### Quickstart (Docker Compose)

The easiest way to run the full AegisOS stack locally is using Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aegisos/aegisos.git
    cd aegisos
    ```

2.  **Start the infrastructure:**
    ```bash
    docker-compose up -d
    ```
    This will start the API Gateway, Worker nodes, Dashboard, PostgreSQL, Neo4j, Redis, Qdrant, and MinIO.

3.  **Access the Dashboard:**
    Navigate to `http://localhost:3000`

4.  **Access the API Documentation:**
    Navigate to `http://localhost:8000/docs`

### Development Setup

To develop locally without Docker (or pointing to local Docker services):

1.  **Install dependencies:**
    ```bash
    make install-all
    ```

2.  **Run migrations:**
    ```bash
    make migrate
    ```

3.  **Start the development server:**
    ```bash
    make dev
    ```

## Documentation

*   **Architecture Decisions**: `/research/architecture_decisions.md`
*   **Research Paper References**: `/research/paper_references.md`

## License

MIT License. See `LICENSE` for details.
