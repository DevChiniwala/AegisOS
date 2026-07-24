# Contributing to AegisOS

Thank you for your interest in contributing to AegisOS! This guide will help you get started.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/DevChiniwala/AegisOS.git
cd AegisOS

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with all extras
pip install -e ".[all]"

# Copy environment configuration
cp .env.example .env

# Start infrastructure services
docker compose up -d redis postgres

# Run tests
pytest tests/unit/ -v

# Start the API
aegis serve --reload
```

## Project Structure

```
AegisOS/
├── apps/           # Application entrypoints (API, CLI, dashboard)
├── core/           # Shared infrastructure (config, events, schemas, telemetry)
├── models/         # ML models (ensemble, GNN, autoencoder)
├── services/       # Domain services (agents, graph, risk, knowledge)
├── packages/       # Distributable packages (SDK, MCP server)
├── tests/          # Test suites (unit, integration, e2e)
└── infrastructure/ # Docker, k8s, observability configs
```

## Making Changes

1. **Create a branch** from `main`
2. **Write tests** for new functionality
3. **Run the test suite**: `pytest tests/unit/ -v`
4. **Run linting**: `ruff check .`
5. **Submit a PR** with a clear description

## Code Standards

- Python 3.11+
- Type hints on all public functions
- No eval(), exec(), or dynamic code execution
- Pydantic models for API boundaries
- Structured logging via `core.utils.logging`
- Async-first for I/O operations

## Commit Messages

Follow conventional commits:
```
feat(scope): description
fix(scope): description
docs(scope): description
test(scope): description
refactor(scope): description
```

## Areas for Contribution

- **ML Models**: New fraud detection algorithms, model calibration
- **Agents**: New investigation agents, improved reasoning
- **Graph Engine**: GNN architectures, community detection algorithms
- **Frontend**: Dashboard components, visualizations
- **Documentation**: Guides, examples, API documentation
- **Testing**: Integration tests, E2E tests, property-based testing
