from opentelemetry.exporter.zipkin.json import ZipkinExporter


def create_telemetry_exporter():
    return ZipkinExporter()
