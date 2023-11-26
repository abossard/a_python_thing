import os

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from pizzalibrary import create_telemetry_exporter
from uvicorn import run

from pizza_shop import app

exporter = create_telemetry_exporter()

tracer = TracerProvider(resource=Resource.create({SERVICE_NAME: "pizza-shop"}))
tracer.add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)
tracer.add_span_processor(
    BatchSpanProcessor(exporter)
)

FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)


port = int(os.getenv('PORT', 8000))
host = os.getenv('HOST', "0.0.0.0")

run(app, host=host, port=port)
