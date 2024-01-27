import logging
import os

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry import configure_azure_monitor
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


def setup_telemetry(service_name, service_instance_id, enable_console=False):
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_INSTANCE_ID: service_instance_id,
    })

    # looking for OLTP endpoint
    oltp_endpoint = os.environ.get("OLTP_ENDPOINT")
    oltp_auth_key = os.environ.get("OLTP_AUTH_KEY")
    application_insights_connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

    tracer_provider = TracerProvider(resource=resource)
    logger_provider = LoggerProvider(resource=resource)

    if oltp_endpoint and oltp_auth_key:
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        print("Using OTLP endpoint: " + oltp_endpoint)

        set_logger_provider(logger_provider)

        url = 'http://localhost:5080/api/default/v1/traces'
        headers = {"Authorization": "Basic " + oltp_auth_key}

        exporter = OTLPSpanExporter(endpoint=oltp_endpoint + '/traces', headers=headers)
        log_exporter = OTLPLogExporter(endpoint=oltp_endpoint + "/logs", headers=headers)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
        oltp_log_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        logging.getLogger().addHandler(oltp_log_handler)
        logging.getLogger().setLevel(logging.NOTSET)
        span_processor = BatchSpanProcessor(exporter)

        # add the span processor to the tracer provider
        tracer_provider.add_span_processor(span_processor)

        # set the tracer provider as the global provider
        trace.set_tracer_provider(tracer_provider)
    elif application_insights_connection_string:

        print("Using Application Insights endpoint: " + application_insights_connection_string)
        settings.tracing_implementation = OpenTelemetrySpan
        configure_azure_monitor(
            connection_string=application_insights_connection_string,
            resource=resource,
            logger_name=service_name
        )

    else:
        enable_console = True
    if enable_console:
        from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        print("Using Console logging")
        span_exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(span_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)

        metrics_exporter = ConsoleMetricExporter()
        reader = PeriodicExportingMetricReader(metrics_exporter, export_interval_millis=60000)
        metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

    azure_sdk_tracing_implementation = os.environ.get("AZURE_SDK_TRACING_IMPLEMENTATION")
    if azure_sdk_tracing_implementation:
        print("AZURE_SDK_TRACING_IMPLEMENTATION is set to:", azure_sdk_tracing_implementation)

    logging.getLogger().info("Tracing and logging initialized")
