"""
OpenTelemetry instrumentation for AegisOS.

Provides distributed tracing across the scoring pipeline, agent orchestration,
and graph queries. Exports to OTLP endpoint in production or stdout in development.
"""
import os
from typing import Optional
from core.utils.logging import get_logger

logger = get_logger(__name__)

_tracer = None


def setup_tracing(service_name: str = "aegisos-api") -> Optional[object]:
    """
    Initialize OpenTelemetry tracing. Returns the tracer provider or None
    if opentelemetry is not installed.
    """
    global _tracer
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
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
