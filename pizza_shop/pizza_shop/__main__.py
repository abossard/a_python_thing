import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from uvicorn import run

from pizza_shop import app

tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "pizza-shop"}))

url = 'http://localhost:5080/api/default/v1/traces'
headers = {"Authorization": "Basic cm9vdEBleGFtcGxlLmNvbTp1cFA1ZlVnWElqcm9iT3JX"}

exporter = OTLPSpanExporter(endpoint=url, headers=headers)

# create a span processor to send spans to the exporter
span_processor = BatchSpanProcessor(exporter)

# add the span processor to the tracer provider
tracer_provider.add_span_processor(span_processor)

# set the tracer provider as the global provider
trace.set_tracer_provider(tracer_provider)

# Add auto-instrumentation for FastAPI on the app
FastAPIInstrumentor().instrument_app(app)

port = int(os.getenv('PORT', 8000))
host = os.getenv('HOST', "0.0.0.0")
run(app, host=host, port=port)
