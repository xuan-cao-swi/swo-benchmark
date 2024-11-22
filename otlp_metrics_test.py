from os import environ
import time
from typing import Iterable
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader
)

service_name = 'xuan-ruby-benchmark'
resource = Resource.create(
    attributes={
        "service.name": service_name,
    }
)

api_token = environ.get("API_TOKEN")
exporter_console = ConsoleMetricExporter()
exporter =  OTLPMetricExporter(
    endpoint="otel.collector.na-01.st-ssp.solarwinds.com:443",
    insecure=False,
    headers={
        "authorization": f"Bearer {api_token}"
    }
)

reader_console = PeriodicExportingMetricReader(
    exporter_console,
    export_interval_millis=5_000,
)

reader = PeriodicExportingMetricReader(
    exporter,
    export_interval_millis=5_000,
)

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[reader_console, reader],
)

metrics.set_meter_provider(meter_provider)
otel_meter = meter_provider.get_meter("benchmark-always-sample")

http_response_time_with_apm = otel_meter.create_histogram(
    name="xuan.ruby.response.time.test_metrics",
    description="measures the duration of the inbound HTTP request",
    unit="ms")

while True:
    http_response_time_with_apm.record(5)
    time.sleep(60)
    print('next recoding')


