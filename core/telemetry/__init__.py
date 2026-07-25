"""
OpenTelemetry instrumentation + Prometheus metrics for AegisOS.

Provides:
- Distributed tracing (OTLP / console)
- Prometheus metrics (counters, histograms, gauges)
- FastAPI auto-instrumentation
"""
import os
import time
from typing import Optional

from core.utils.logging import get_logger

logger = get_logger(__name__)

_tracer = None


def setup_tracing(service_name: str = "aegisos-api") -> Optional[object]:
    """Initialize OpenTelemetry tracing."""
    global _tracer
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )

        resource = Resource.create({
            "service.name": service_name,
            "service.version": "0.1.0",
            "deployment.environment": os.getenv("AEGIS_ENV", "development"),
        })

        provider = TracerProvider(resource=resource)

        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info("OTLP exporter configured", endpoint=otlp_endpoint)
            except ImportError:
                logger.warning("OTLP exporter not available, falling back to console")
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            if os.getenv("AEGIS_ENV") != "production":
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(__name__)

        logger.info("OpenTelemetry tracing initialized", service=service_name)
        return provider

    except ImportError:
        logger.info("opentelemetry not installed — tracing disabled")
        return None


def instrument_fastapi(app) -> None:
    """Attach OpenTelemetry auto-instrumentation to FastAPI app."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI OpenTelemetry instrumentation attached")
    except ImportError:
        pass


def get_tracer():
    """Get the configured tracer, or a no-op proxy."""
    global _tracer
    if _tracer:
        return _tracer
    try:
        from opentelemetry import trace
        return trace.get_tracer(__name__)
    except ImportError:
        return _NoOpTracer()


class _NoOpSpan:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def set_attribute(self, key, value):
        pass

    def add_event(self, name, attributes=None):
        pass


class _NoOpTracer:
    def start_as_current_span(self, name, **kwargs):
        return _NoOpSpan()


# --- Prometheus Metrics ---

class _MetricRegistry:
    """Application metrics for AegisOS."""

    def __init__(self):
        self._transactions_scored = 0
        self._transactions_blocked = 0
        self._scoring_latencies: list[float] = []
        self._investigation_durations: list[float] = []
        self._llm_tokens: dict[str, int] = {}
        self._model_drift_scores: dict[str, float] = {}
        self._active_investigations = 0
        self._start_time = time.time()

    def record_transaction_scored(self, risk_score: float, latency_ms: float):
        self._transactions_scored += 1
        self._scoring_latencies.append(latency_ms)
        if len(self._scoring_latencies) > 10000:
            self._scoring_latencies = self._scoring_latencies[-5000:]
        if risk_score > 0.85:
            self._transactions_blocked += 1

    def record_investigation_duration(self, duration_seconds: float):
        self._investigation_durations.append(duration_seconds)
        if len(self._investigation_durations) > 1000:
            self._investigation_durations = self._investigation_durations[-500:]

    def record_llm_tokens(self, provider: str, model: str, tokens: int):
        key = f"{provider}/{model}"
        self._llm_tokens[key] = self._llm_tokens.get(key, 0) + tokens

    def set_model_drift(self, model_name: str, drift_score: float):
        self._model_drift_scores[model_name] = drift_score

    def increment_active_investigations(self):
        self._active_investigations += 1

    def decrement_active_investigations(self):
        self._active_investigations = max(0, self._active_investigations - 1)

    def get_metrics(self) -> dict:
        latencies = self._scoring_latencies
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else avg_latency
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else p95_latency

        inv_durations = self._investigation_durations
        avg_inv = sum(inv_durations) / len(inv_durations) if inv_durations else 0

        return {
            "transactions_scored_total": self._transactions_scored,
            "transactions_blocked_total": self._transactions_blocked,
            "scoring_latency_avg_ms": round(avg_latency, 2),
            "scoring_latency_p95_ms": round(p95_latency, 2),
            "scoring_latency_p99_ms": round(p99_latency, 2),
            "investigation_duration_avg_s": round(avg_inv, 2),
            "active_investigations": self._active_investigations,
            "llm_tokens_by_model": dict(self._llm_tokens),
            "model_drift_scores": dict(self._model_drift_scores),
            "uptime_seconds": round(time.time() - self._start_time, 0),
        }

    def prometheus_text(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        m = self.get_metrics()

        lines.append("# HELP aegis_transactions_scored_total Total transactions scored")
        lines.append("# TYPE aegis_transactions_scored_total counter")
        lines.append(f"aegis_transactions_scored_total {m['transactions_scored_total']}")

        lines.append("# HELP aegis_transactions_blocked_total Transactions blocked due to high risk")
        lines.append("# TYPE aegis_transactions_blocked_total counter")
        lines.append(f"aegis_transactions_blocked_total {m['transactions_blocked_total']}")

        lines.append("# HELP aegis_scoring_latency_seconds Transaction scoring latency")
        lines.append("# TYPE aegis_scoring_latency_seconds summary")
        lines.append(f'aegis_scoring_latency_seconds{{quantile="0.5"}} {m["scoring_latency_avg_ms"] / 1000:.6f}')
        lines.append(f'aegis_scoring_latency_seconds{{quantile="0.95"}} {m["scoring_latency_p95_ms"] / 1000:.6f}')
        lines.append(f'aegis_scoring_latency_seconds{{quantile="0.99"}} {m["scoring_latency_p99_ms"] / 1000:.6f}')

        lines.append("# HELP aegis_investigation_duration_seconds Investigation duration")
        lines.append("# TYPE aegis_investigation_duration_seconds gauge")
        lines.append(f"aegis_investigation_duration_seconds {m['investigation_duration_avg_s']:.3f}")

        lines.append("# HELP aegis_active_investigations Current active investigations")
        lines.append("# TYPE aegis_active_investigations gauge")
        lines.append(f"aegis_active_investigations {m['active_investigations']}")

        for model_key, tokens in m["llm_tokens_by_model"].items():
            provider, model = model_key.split("/", 1) if "/" in model_key else (model_key, "unknown")
            lines.append(f'aegis_llm_tokens_total{{provider="{provider}",model="{model}"}} {tokens}')

        for model_name, drift in m["model_drift_scores"].items():
            lines.append(f'aegis_model_drift_score{{model="{model_name}"}} {drift:.4f}')

        return "\n".join(lines) + "\n"


metrics = _MetricRegistry()
