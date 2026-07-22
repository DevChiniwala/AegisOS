# AegisOS — Implementation Tasks

## Workstream 1: Foundation & Core Kernel
- [ ] `pyproject.toml` — Project config, dependencies
- [ ] `Makefile` — Development commands
- [ ] `core/config/settings.py` — Configuration management
- [ ] `core/schemas/` — All Pydantic schemas (transaction, entity, risk, investigation, events)
- [ ] `core/database/` — Database adapters, ORM models, migrations
- [ ] `core/security/` — JWT, RBAC, encryption, audit
- [ ] `core/events/` — Event bus abstraction (memory, redis, kafka)
- [ ] `core/utils/` — Shared utilities

## Workstream 2: Feature Engineering & Risk Scoring
- [ ] `services/feature_engine/engine.py` — Feature pipeline orchestrator
- [ ] `services/feature_engine/extractors/` — All feature extractors (7 types)
- [ ] `services/feature_engine/store.py` — Feature store
- [ ] `services/risk_engine/engine.py` — Tiered scoring pipeline
- [ ] `services/risk_engine/rules/` — Rule engine + YAML rules
- [ ] `services/risk_engine/ensemble.py` — SHAP-guided adaptive ensemble
- [ ] `models/ensemble/` — XGBoost, LightGBM, CatBoost, IsolationForest, Autoencoder
- [ ] `models/temporal/` — Temporal transformer, sequence encoder

## Workstream 3: Graph Intelligence
- [ ] `services/graph_engine/engine.py` — Graph intelligence core
- [ ] `services/graph_engine/schema.py` — Node/edge type definitions
- [ ] `services/graph_engine/algorithms/` — All graph algorithms (5 types)
- [ ] `services/graph_engine/store.py` — Graph store abstraction
- [ ] `models/graph_models/` — GraphSAGE, GAT, TGN, HGNN

## Workstream 4: Investigation & Memory
- [ ] `services/agents/orchestrator.py` — Investigation state machine
- [ ] `services/agents/agents/` — All 9 agent implementations
- [ ] `services/memory/engine.py` — Unified memory interface
- [ ] `services/memory/vector_store.py` — Vector memory (FAISS/Qdrant)
- [ ] `services/memory/knowledge_graph.py` — Fraud pattern KG
- [ ] `services/memory/case_store.py` — Case history
- [ ] `services/explainability/` — SHAP, counterfactual, narrator

## Workstream 5: API Gateway & Services
- [ ] `apps/api/main.py` — FastAPI app setup
- [ ] `apps/api/routes/` — All API routes (8 route groups)
- [ ] `apps/api/middleware/` — Rate limiting, audit, CORS
- [ ] `services/streaming/` — Stream processor, consumers, producers
- [ ] `services/compliance/engine.py` — AML, sanctions, SAR
- [ ] `services/notification/engine.py` — Multi-channel alerts
- [ ] `services/behavioral_ai/` — Behavioral profiling & anomaly

## Workstream 6: Data, Infrastructure & Docs
- [ ] `datasets/generator.py` — Synthetic data generator
- [ ] `datasets/scenarios/` — Pre-built fraud scenarios
- [ ] `docker-compose.yml` — Full stack compose
- [ ] `infrastructure/docker/` — Dockerfiles
- [ ] `.github/workflows/` — CI/CD pipelines
- [ ] `README.md` — Professional README
- [ ] `research/` — Architecture decisions, paper references

## Workstream 7: Frontend Dashboard
- [ ] Next.js project setup with TypeScript + TailwindCSS + shadcn/ui
- [ ] Fraud Dashboard page — KPIs, risk heatmap, live feed
- [ ] Graph Explorer page — Interactive React Flow visualization
- [ ] Investigation Workspace — Case management + timeline
- [ ] Live Streaming Panel — WebSocket transaction feed
- [ ] Model Monitoring page — Performance metrics
