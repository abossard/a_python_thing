from opentelemetry import trace
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource


def configure_opentelemetry(name: str):
    # Create a Zipkin exporter
    exporter = ZipkinExporter()

    # Create a BatchSpanProcessor and add the exporter
    span_processor = BatchSpanProcessor(exporter)

    # Create a TracerProvider with the configured exporter and span processor
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": name})))
    trace.get_tracer_provider().add_span_processor(span_processor)
