import logging
import os
from opentelemetry import trace
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_INSTANCE_ID
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import metrics
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider


def configure_opentelemetry(name: str):

    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: name})))

    # Create a Zipkin exporter
    exporter = ZipkinExporter()

    # Create a BatchSpanProcessor and add the exporter
    span_processor = BatchSpanProcessor(exporter)

    # Create a TracerProvider with the configured exporter and span processor
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(span_processor)
    # application_insights_connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    # if application_insights_connection_string:
    #     from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
    #     from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
    #     from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    #     print("Using Application Insights endpoint: " + application_insights_connection_string)

    #     logger_provider = LoggerProvider()
    #     set_logger_provider(logger_provider)

    #     logs_exporter = AzureMonitorLogExporter(
    #         connection_string=application_insights_connection_string
    #     )
    #     logger_provider.add_log_record_processor(BatchLogRecordProcessor(logs_exporter))
    #     handler = LoggingHandler()

    #     # Attach LoggingHandler to root logger
    #     logging.getLogger().addHandler(handler)
    #     logging.getLogger().setLevel(logging.NOTSET)

    #     metrics_exporter = AzureMonitorMetricExporter(
    #         connection_string=application_insights_connection_string
    #     )

    #     reader = PeriodicExportingMetricReader(metrics_exporter, export_interval_millis=5000)
    #     metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

    #     span_exporter = AzureMonitorTraceExporter(connection_string=application_insights_connection_string)
    #     span_processor = BatchSpanProcessor(span_exporter)
    #     tracer_provider.add_span_processor(span_processor)
    #     trace.set_tracer_provider(tracer_provider)
