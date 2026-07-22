<p align="center">
  <img src="docs/assets/banner.svg" alt="AegisOS Banner" width="100%"/>
</p>

<p align="center">
  <a href="#quickstart"><img src="https://img.shields.io/badge/Quick_Start-blue?style=for-the-badge&logo=rocket&logoColor=white" alt="Quick Start"/></a>
  <a href="#architecture"><img src="https://img.shields.io/badge/Architecture-purple?style=for-the-badge&logo=blueprint&logoColor=white" alt="Architecture"/></a>
  <a href="#features"><img src="https://img.shields.io/badge/Features-green?style=for-the-badge&logo=sparkles&logoColor=white" alt="Features"/></a>
  <a href="https://github.com/DevChiniwala/AegisOS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-yellow?style=for-the-badge" alt="License"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js_14-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Neo4j-4581C3?style=flat-square&logo=neo4j&logoColor=white" alt="Neo4j"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
</p>

---

## What is AegisOS?

**AegisOS** is the world's most advanced open-source fraud intelligence platform. Built for enterprise scale, it moves beyond simple classification to provide a comprehensive, multi-agent AI system capable of **autonomous fraud detection, investigation, reasoning, and reporting**.

Unlike traditional systems that rely on static thresholds or a single ML classifier, AegisOS employs a layered intelligence architecture that combines **rule-based fast-path evaluation**, **SHAP-weighted ensemble models**, **graph-based fraud ring detection**, **behavioral AI profiling**, and **9 autonomous AI agents** that investigate flagged transactions and generate audit-ready Suspicious Activity Reports (SARs).

### Who is this for?

| Role | Value |
|------|-------|
| **Fintech Companies** | Drop-in fraud detection with sub-50ms latency |
| **Banks & Payment Processors** | AML/CTR/SAR compliance automation |
| **Data Scientists** | Production-grade ML pipeline with SHAP explainability |
| **Security Researchers** | Graph intelligence for fraud ring discovery |
| **Regulators** | Transparent, auditable AI decision-making |

---

## Architecture

<p align="center">
  <img src="docs/assets/architecture-overview.svg" alt="System Architecture" width="100%"/>
</p>

AegisOS is built as an **event-driven microservices** architecture with 5 distinct layers:

| Layer | Responsibility | Key Components |
|-------|---------------|----------------|
| **Client** | User interfaces & external integrations | Next.js Dashboard, WebSocket Streams, REST API, Graph Explorer |
| **Gateway** | Security, routing, observability | JWT Auth, Rate Limiting, Request Tracing, Audit Logging |
| **Intelligence** | Core fraud detection & investigation | Feature Engine, Risk Engine, Graph Intelligence, Behavioral AI, Multi-Agent System |
| **ML** | Predictive models & explainability | XGBoost, LightGBM, CatBoost, Isolation Forest, SHAP |
| **Data** | Polyglot persistence | PostgreSQL, Neo4j, Redis, Qdrant, MinIO |

---

## Data Flow

<p align="center">
  <img src="docs/assets/data-flow.svg" alt="Transaction Scoring Pipeline" width="100%"/>
</p>

### Transaction Lifecycle

```
1. INGEST     Transaction arrives via REST API or Kafka stream
                 ↓ validate + enrich with entity context
2. EXTRACT    60+ features computed in parallel (<5ms)
                 ↓ transaction, device, temporal, behavioral, graph
3. FAST PATH  YAML rule engine evaluates 10 pre-configured rules (<5ms)
                 ↓ if rule triggers → immediate BLOCK/FLAG
4. ML SCORE   Adaptive ensemble: 4 models with SHAP-weighted voting
                 ↓ Platt-calibrated probability output
5. VERDICT    Risk level assigned: ALLOW | FLAG | BLOCK
                 ↓ if score > 0.7 → trigger full investigation
6. INVESTIGATE  9 AI agents dispatched by Supervisor
                 ↓ parallel analysis across all intelligence engines
7. COMPILE    Evidence chain assembled, confidence scored
                 ↓ Decision Agent renders final verdict
8. OUTPUT     Investigation case created with full audit trail
                 ↓ SAR auto-generated if criteria met
9. COMPLY     Regulatory actions: AML screening, CTR filing, KYC checks
```

### Latency Guarantees

| Path | Latency | Description |
|------|---------|-------------|
| Fast Path (Rule Hit) | **< 20ms** | Immediate BLOCK for known fraud patterns |
| ML Scoring | **< 50ms** | Full ensemble with calibration |
| Investigation | **< 5s** | 9 agents analyzing in parallel |

---

<a id="features"></a>
## Features

### Tiered Risk Scoring Engine

The risk engine operates in two tiers for optimal latency:

**Fast Path** — YAML-defined rules evaluated in < 5ms:
```yaml
rules:
  - name: amount_limit
    action: BLOCK
    condition: features.get('is_large_amount', 0.0) == 1.0 or features.get('amount_log', 0) > 10.8
    reason: Transaction amount exceeds absolute limit

  - name: velocity_check
    action: FLAG
    condition: features.get('amount_zscore', 0.0) > 4.0
    reason: Extreme deviation from historical spending pattern
```

**ML Ensemble** — SHAP-weighted adaptive scoring:
- **XGBoost** — Gradient boosted trees (scale_pos_weight=10 for class imbalance)
- **LightGBM** — Leaf-wise growth (is_unbalance=True)
- **CatBoost** — Symmetric trees with native categorical handling
- **Isolation Forest** — Unsupervised anomaly detection

Model agreement is measured via cosine similarity of SHAP vectors. Higher agreement = higher weight. Raw scores are Platt-calibrated to true probabilities.

---

### Graph Intelligence Engine

```
                    ┌─────────────────────────────────────┐
                    │       Knowledge Graph (Neo4j)        │
                    │                                     │
                    │   [User]──PAID_TO──[Merchant]       │
                    │     │                  │            │
                    │   OWNS              RECEIVED        │
                    │     │                  │            │
                    │   [Device]      [Transaction]       │
                    │     │                  │            │
                    │   LOGGED_IN_FROM    FLAGGED         │
                    │     │                  │            │
                    │   [IP Address]    [Alert]           │
                    └─────────────────────────────────────┘
```

| Algorithm | Purpose | Implementation |
|-----------|---------|----------------|
| **Louvain Community Detection** | Discover fraud rings | `services/graph_engine/algorithms/community_detection.py` |
| **Risk Propagation** | Spread risk scores through graph edges | Belief propagation with configurable decay (0.85) |
| **Shortest Path Analysis** | Trace money flow between entities | BFS with depth-limited exploration |
| **Circular Flow Detection** | Identify round-tripping patterns | Cycle detection in directed graph |
| **PageRank** | Identify hub entities | NetworkX PageRank on transaction graph |
| **Degree Centrality** | Measure entity connectivity | Used as graph feature for ML models |

---

### Multi-Agent Investigation System

When a transaction scores above the investigation threshold (0.7), the **Supervisor Agent** orchestrates 9 specialized AI agents:

```
                         ┌──────────────────┐
                         │   SUPERVISOR     │
                         │   (Orchestrator) │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
     ┌────────┴────────┐  ┌──────┴──────┐  ┌────────┴────────┐
     │  Tx Investigator │  │Graph Detective│  │Behavior Analyst │
     │  Amount, Z-score │  │Ring proximity │  │Temporal patterns│
     │  Velocity, Type  │  │Shared entities│  │Spending habits  │
     └─────────────────┘  └─────────────┘  └─────────────────┘
              │                   │                   │
     ┌────────┴────────┐  ┌──────┴──────┐  ┌────────┴────────┐
     │Evidence Collector│  │Risk Assessor │  │Compliance Officer│
     │Gather artifacts  │  │Score & weigh │  │AML/KYC/SAR check│
     └─────────────────┘  └─────────────┘  └─────────────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │       Decision Agent       │
                    │  Final verdict + confidence│
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │     Report Generator       │
                    │   SAR + Audit narrative    │
                    └───────────────────────────┘
```

Each agent:
- Receives full investigation context (transaction, features, graph data, behavioral profile)
- Produces a **Finding** with confidence score and evidence references
- Operates independently — no shared state between agents
- Results are compiled by the Decision Agent for final verdict

---

### Explainable AI (XAI)

Every decision in AegisOS comes with a complete explanation:

| Component | What it provides |
|-----------|-----------------|
| **SHAP TreeExplainer** | Per-feature contribution to the fraud score |
| **Counterfactual Reasoning** | "What would need to change for this to be legitimate?" |
| **Natural Language Narrative** | Human-readable explanation of the decision |
| **Model Agreement** | Which models agreed/disagreed and why |
| **Confidence Score** | Calibrated probability of fraud |
| **Evidence Chain** | Traceable path from raw data to verdict |

---

### Real-Time Dashboard

The Next.js 14 dashboard provides a professional fraud intelligence interface:

| Page | Capabilities |
|------|-------------|
| **Dashboard** | KPI cards, transaction volume charts, risk heatmap, alert feed |
| **Transactions** | Filterable data table, risk score visualization, SHAP waterfall charts |
| **Investigations** | Case timeline, agent actions, evidence cards, SAR generation |
| **Graph Explorer** | Interactive React Flow canvas, entity search, fraud ring visualization |
| **Live Feed** | Real-time WebSocket transaction stream with auto-scroll |
| **Models** | Performance metrics, drift indicators, latency charts, model reload |
| **Settings** | Risk thresholds, system health, audit log, user management |

**Design System**: Dark-mode finance theme with risk-colored accents (green → amber → red) and responsive layout.

---

### Compliance Engine

| Regulation | Implementation |
|-----------|----------------|
| **AML** | Transaction monitoring with aggregation windows |
| **CTR** | Auto-flag transactions > $10,000 |
| **SAR** | Auto-generate Suspicious Activity Reports |
| **KYC** | Entity verification and risk profiling |
| **OFAC** | Sanctions screening against watchlists |
| **PEP** | Politically Exposed Persons detection |
| **PSD2** | European payment services compliance |
| **GDPR** | Data handling for EU transactions |

---

## Tech Stack

<p align="center">
  <img src="docs/assets/tech-stack.svg" alt="Technology Stack" width="100%"/>
</p>

<details>
<summary><strong>Complete Dependency List</strong></summary>

### Backend
| Package | Purpose |
|---------|---------|
| FastAPI | Async web framework with automatic OpenAPI docs |
| Pydantic v2 | Data validation and settings management |
| SQLAlchemy 2.0 | Async ORM with PostgreSQL/asyncpg |
| Alembic | Database migrations |
| Celery | Distributed task queue for background workers |
| Redis (aioredis) | Caching, event streaming, pub/sub |
| neo4j (async driver) | Graph database operations |
| NetworkX | In-memory graph algorithms |
| python-community-louvain | Community detection |
| XGBoost / LightGBM / CatBoost | Gradient boosted ensemble |
| scikit-learn | Isolation Forest, preprocessing |
| SHAP | Model explainability |
| NumPy | Numerical computing |
| joblib | Model serialization |
| PyYAML | Rule engine configuration |
| python-jose / passlib | JWT authentication |
| uvicorn | ASGI server |

### Frontend
| Package | Purpose |
|---------|---------|
| Next.js 14 | React framework with App Router |
| TypeScript 5 | Type safety |
| TailwindCSS 3.4 | Utility-first styling |
| shadcn/ui | Accessible component primitives |
| @tanstack/react-query 5 | Server state management |
| @tanstack/react-table 8 | Headless data tables |
| React Flow 11 | Graph visualization canvas |
| Recharts 2 | Charts and data visualization |
| Framer Motion 11 | Animations |
| Zustand 4 | Client state (notifications) |
| Axios | HTTP client with interceptors |
| next-themes | Dark/light mode |
| Lucide React | Icon system |
| Sonner | Toast notifications |

### Infrastructure
| Tool | Purpose |
|------|---------|
| Docker + Docker Compose | Containerization (7 services) |
| Kubernetes + Helm | Production orchestration |
| Terraform | Infrastructure as Code |
| GitHub Actions | CI/CD pipeline |
| Prometheus + Grafana | Monitoring |

</details>

---

## Project Structure

```
AegisOS/
├── apps/
│   ├── api/                        # FastAPI application
│   │   ├── main.py                 # App entrypoint + lifespan
│   │   ├── dependencies.py         # Dependency injection (7 engines)
│   │   ├── middleware.py           # Rate limit, audit, timing, request ID
│   │   └── routes/                 # REST endpoints (9 routers)
│   │       ├── transactions.py
│   │       ├── investigations.py
│   │       ├── graph.py
│   │       ├── streaming.py        # WebSocket endpoints
│   │       └── ...
│   └── dashboard/                  # Next.js 14 frontend
│       ├── src/
│       │   ├── app/                # App Router pages (12 routes)
│       │   ├── components/         # 75+ React components
│       │   ├── hooks/              # Custom hooks (auth, websocket, debounce)
│       │   ├── lib/                # API client, utils, mock data
│       │   ├── providers/          # Auth, Query, Theme, Toast
│       │   └── types/              # TypeScript type definitions
│       └── Dockerfile              # Multi-stage production build
│
├── core/                           # Shared core modules
│   ├── config/                     # Settings (Pydantic BaseSettings)
│   ├── schemas/                    # Pydantic models (transaction, entity, investigation)
│   ├── events/                     # Event bus (Redis + InMemory implementations)
│   ├── database/                   # SQLAlchemy sessions + Alembic
│   └── utils/                      # Logging, helpers, timing
│
├── models/                         # Machine Learning
│   ├── base.py                     # FraudModel protocol + ModelRegistry
│   └── ensemble/
│       ├── xgboost_model.py        # XGBoost with SHAP explain()
│       ├── lightgbm_model.py       # LightGBM with SHAP explain()
│       ├── catboost_model.py       # CatBoost classifier
│       ├── isolation_forest.py     # Unsupervised anomaly detection
│       └── autoencoder.py          # Deep learning anomaly detector
│
├── services/                       # Business logic services
│   ├── agents/                     # Multi-Agent Investigation
│   │   ├── orchestrator.py         # Supervisor + dispatch logic
│   │   └── agents/                 # 9 specialized agent implementations
│   │       ├── transaction_investigator.py
│   │       ├── graph_detective.py
│   │       ├── behavior_analyst.py
│   │       ├── evidence_collector.py
│   │       ├── risk_assessor.py
│   │       ├── compliance_officer.py
│   │       ├── decision_agent.py
│   │       ├── supervisor.py
│   │       └── report_generator.py
│   ├── behavioral_ai/             # User behavior profiling
│   ├── compliance/                 # AML/KYC/SAR engine
│   ├── explainability/            # SHAP + counterfactual reasoning
│   ├── feature_engine/            # Real-time feature extraction
│   │   ├── engine.py              # Orchestrates all extractors
│   │   ├── store.py               # Feature store (timezone-safe)
│   │   └── extractors/
│   │       ├── transaction_features.py  # Amount, z-score, ratios
│   │       ├── device_features.py       # Device fingerprinting
│   │       ├── temporal_features.py     # Time-based patterns
│   │       └── graph_features.py        # Centrality, PageRank, shared entities
│   ├── graph_engine/              # Graph intelligence
│   │   ├── engine.py              # Fraud rings, risk propagation, path finding
│   │   ├── store.py               # NetworkX + Neo4j dual-store
│   │   └── algorithms/
│   │       ├── community_detection.py   # Louvain + label propagation
│   │       ├── risk_propagation.py      # Belief propagation with decay
│   │       ├── path_analysis.py         # Shortest path + cycle detection
│   │       ├── centrality.py            # Degree, betweenness, PageRank
│   │       └── embeddings.py            # Graph neural network embeddings
│   ├── memory/                    # AI memory system
│   │   ├── engine.py              # Vector search + knowledge graph
│   │   ├── vector_store.py        # Embedding similarity (Qdrant)
│   │   ├── knowledge_graph.py     # Fraud pattern typologies
│   │   └── case_store.py          # Historical case retrieval
│   ├── notification/              # Alert dispatch
│   └── risk_engine/               # Core scoring
│       ├── engine.py              # Tiered scoring orchestrator
│       ├── ensemble.py            # SHAP agreement + Platt calibration
│       └── rules/
│           ├── rule_engine.py     # YAML rule evaluator
│           └── rules.yaml         # 10 pre-configured detection rules
│
├── infrastructure/                # Deployment configs
│   ├── docker/                    # Dockerfiles (API, Worker, etc.)
│   ├── kubernetes/                # Helm charts
│   └── terraform/                 # Cloud IaC
│
├── tests/                         # Test suite
│   └── unit/
│       ├── test_rule_engine.py
│       ├── test_compliance.py
│       ├── test_feature_store.py
│       └── test_feature_extractors.py
│
├── docker-compose.yml             # Full dev stack (7 services)
├── Makefile                       # Development commands
├── pyproject.toml                 # Python project config
└── .gitignore                     # Standard ignores
```

---

<a id="quickstart"></a>
## Quickstart

### Prerequisites

- **Docker** & Docker Compose (v2)
- **Python 3.11+** (for local development)
- **Node.js 20+** (for dashboard development)

### One-Command Start (Docker)

```bash
git clone https://github.com/DevChiniwala/AegisOS.git
cd AegisOS
docker-compose up -d
```

This starts **7 services**: API Gateway, Celery Worker, Dashboard, PostgreSQL, Neo4j, Redis, Qdrant, and MinIO.

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http://localhost:3000 | Fraud intelligence UI |
| API Docs | http://localhost:8000/docs | Swagger/OpenAPI explorer |
| Neo4j Browser | http://localhost:7474 | Graph visualization |
| MinIO Console | http://localhost:9001 | Object storage admin |

### Local Development

```bash
# Backend
make install-all          # Install all Python dependencies
make migrate              # Run database migrations
make dev                  # Start FastAPI dev server (port 8000)

# Frontend (separate terminal)
cd apps/dashboard
npm install
npm run dev               # Start Next.js dev server (port 3000)

# Tests
make test                 # Run full test suite
```

### Environment Variables

Copy `.env.local.example` to configure:

```env
# Core
AEGIS_DATABASE_URL=postgresql+asyncpg://aegis:aegis_secret@localhost:5432/aegisdb
AEGIS_REDIS_URL=redis://localhost:6379/0
AEGIS_NEO4J_URI=bolt://localhost:7687
AEGIS_NEO4J_USER=neo4j
AEGIS_NEO4J_PASSWORD=aegis_neo4j
AEGIS_QDRANT_URL=http://localhost:6333
AEGIS_SECURITY_SECRET_KEY=your-secret-key

# Dashboard
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/transactions/score` | Score a transaction in real-time |
| `GET` | `/api/v1/transactions` | List transactions with filters |
| `GET` | `/api/v1/transactions/{id}` | Get transaction details + SHAP explanation |
| `GET` | `/api/v1/investigations` | List investigation cases |
| `GET` | `/api/v1/investigations/{id}/timeline` | Agent investigation timeline |
| `GET` | `/api/v1/graph/entity/{id}` | Get entity subgraph |
| `GET` | `/api/v1/graph/communities` | Detect fraud rings |
| `GET` | `/api/v1/graph/path/{source}/{target}` | Trace money flow |
| `WS` | `/api/v1/ws/transactions` | Real-time transaction stream |
| `WS` | `/api/v1/ws/alerts` | Real-time alert notifications |
| `GET` | `/api/v1/dashboard/overview` | Dashboard KPIs |
| `GET` | `/api/v1/admin/health` | System health check |

Full interactive documentation available at `/docs` (Swagger UI) when the API is running.

---

## How It Works

### Feature Extraction Pipeline

AegisOS extracts **60+ features** from each transaction in real-time:

| Category | Features | Examples |
|----------|----------|---------|
| **Transaction** | 10 | Amount z-score, log amount, round amount indicator, foreign currency |
| **Device** | 8 | New device flag, device age, emulator detection, OS encoding |
| **Temporal** | 12 | Hour of day, day of week, time since last transaction, velocity |
| **Behavioral** | 15 | Deviation from spending profile, location anomaly, channel change |
| **Graph** | 10 | Degree centrality, PageRank, shared devices, fraud ring proximity |
| **Aggregated** | 8 | 24h/7d/30d transaction counts, cumulative amounts |

All categorical features use **deterministic MD5 encoding** (not Python's non-deterministic `hash()`) for cross-run stability.

### Ensemble Scoring

```
                    ┌─────────────┐
                    │  Features   │
                    │  (60+ dim)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     ┌────┴────┐    ┌─────┴─────┐    ┌────┴────┐
     │ XGBoost │    │  LightGBM │    │ CatBoost│    ┌──────────┐
     │ p₁=0.82 │    │  p₂=0.79  │    │ p₃=0.85│    │IsoForest │
     └────┬────┘    └─────┬─────┘    └────┬────┘    │ p₄=0.71  │
          │                │                │        └────┬─────┘
          └────────────────┼────────────────┘             │
                           │                              │
                    ┌──────┴──────┐                       │
                    │SHAP Agreement│◄──────────────────────┘
                    │cos_sim(shap) │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Weighted   │  score = Σ(wᵢ × pᵢ)
                    │   Average   │  where wᵢ ∝ agreement
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │    Platt    │  P(fraud) = σ(a·score + b)
                    │ Calibration │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   0.83      │ ← calibrated probability
                    │  VERDICT:   │
                    │   BLOCK     │
                    └─────────────┘
```

---

## Fraud Types Detected

| Fraud Type | Detection Method |
|-----------|------------------|
| **Credit Card Fraud** | Behavioral deviation + velocity checks |
| **Account Takeover** | New device/IP + immediate high-value transfer |
| **Money Laundering** | Graph-based ring detection + structuring patterns |
| **Transaction Structuring** | Amount clustering below reporting thresholds |
| **Synthetic Identity** | Graph analysis of shared devices/IPs across identities |
| **Wire Transfer Fraud** | Cross-border anomaly + recipient risk scoring |
| **Merchant Fraud** | Unusual transaction patterns + collusion detection |
| **Friendly Fraud** | Behavioral profiling + chargeback pattern analysis |

---

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests (requires Docker services)
pytest tests/integration -v

# With coverage
pytest --cov=services --cov=core --cov-report=html
```

### Code Quality

```bash
make lint       # ruff check + mypy
make format     # ruff format
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
make migrate
```

---

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d          # Start all services
docker-compose logs -f api    # Follow API logs
docker-compose down           # Stop all services
```

### Kubernetes (Production)

```bash
helm install aegis ./infrastructure/kubernetes/helm \
  --namespace aegis \
  --set api.replicas=3 \
  --set worker.replicas=5
```

### Scaling Considerations

| Component | Horizontal Scaling | Notes |
|-----------|-------------------|-------|
| API Gateway | Stateless, scale freely | Load balancer distributes requests |
| Celery Workers | Scale per queue backlog | Separate queues for scoring vs investigation |
| PostgreSQL | Read replicas | Write to primary, read from replicas |
| Neo4j | Causal clustering | Read replicas for graph queries |
| Redis | Sentinel/Cluster | Streams require cluster mode for partitioning |
| Dashboard | CDN + multiple pods | Static assets served from CDN edge |

---

## Contributing

We welcome contributions! See our development setup above to get started.

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat(scope): add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

### Commit Convention

```
fix(rule-engine): description    # Bug fixes
feat(graph): description         # New features
test(core): description          # Test additions
docs: description                # Documentation
```

---

## Roadmap

- [ ] PyTorch GraphSAGE / GAT for graph embeddings
- [ ] Temporal Graph Networks (TGN) for dynamic fraud patterns
- [ ] LLM-powered natural language investigation narratives
- [ ] Real-time model retraining pipeline
- [ ] Federated learning for cross-institutional models
- [ ] Production Qdrant integration (beyond in-memory)
- [ ] Kafka integration for high-throughput streaming
- [ ] Grafana dashboards + Prometheus metrics

---

## Research & References

AegisOS draws from cutting-edge research in fraud detection:

- **Graph-based Fraud Detection**: Louvain community detection, heterophily-aware GNNs
- **Ensemble Methods**: SHAP-guided dynamic weighting (Lundberg & Lee, 2017)
- **Behavioral Analysis**: Temporal sequence modeling for user profiling
- **Explainable AI**: Counterfactual reasoning for regulatory compliance
- **Multi-Agent Systems**: Specialized agent orchestration patterns

See `/research/` for architecture decision records and paper references.

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built with purpose. Engineered for scale. Designed for trust.</strong>
</p>

<p align="center">
  <a href="https://github.com/DevChiniwala/AegisOS">
    <img src="https://img.shields.io/badge/Star_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
</p>
