import logging
import os

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_INSTANCE_ID
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from uvicorn import run

resource = Resource.create({
    SERVICE_NAME: "pizza-shop",
    SERVICE_INSTANCE_ID: "pizza-shop-1",
})

tracer_provider = TracerProvider(resource=resource)
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

url = 'http://localhost:5080/api/default/v1/traces'
headers = {"Authorization": "Basic cm9vdEBleGFtcGxlLmNvbTp1cFA1ZlVnWElqcm9iT3JX"}

exporter = OTLPSpanExporter(endpoint=url, headers=headers)
log_exporter = OTLPLogExporter(endpoint="http://localhost:5080/api/default/v1/logs", headers=headers)
logger_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
oltp_log_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(oltp_log_handler)

span_processor = SimpleSpanProcessor(exporter)

# add the span processor to the tracer provider
tracer_provider.add_span_processor(span_processor)

# set the tracer provider as the global provider
trace.set_tracer_provider(tracer_provider)

# Add auto-instrumentation for FastAPI on the app


logging.info("Starting application")

from pizza_shop.webapp import app

FastAPIInstrumentor().instrument_app(app)

port = int(os.getenv('PORT', 8000))
host = os.getenv('HOST', "0.0.0.0")
run(app, host=host, port=port)
