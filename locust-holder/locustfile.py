from os import environ
import time
from typing import Iterable

from locust import HttpUser, task, between, events

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
        "sw.data.module": "apm",
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

metrics_name = environ.get("CUSTOM_METRICS_NAME")
if metrics_name == None or metrics_name == '':
    metrics_name = 'xuan.ruby.service.response.time' # let default to this one

http_response_time = otel_meter.create_histogram(
    name=metrics_name,
    description="measures the duration of the inbound HTTP request",
    unit="ms")

locust_wait_time_l = int(environ.get("LOCUST_WAIT_TIME_L"))
locust_wait_time_h = int(environ.get("LOCUST_WAIT_TIME_H"))
metrics_attribute_name = environ.get("METRICS_ATTRIBUTE_NAME")

def debug_response_time(response_time, kw):
    print("\n===========================================\n")
    print(response_time)
    for key, value in kw.items():
        print(f"{key}: {value}")

#  Locust does have an event hook called on_test_start. You can use it to execute code when a test starts. Here’s an example of how to use it:
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    def consume_requests_per_second(
        options: metrics.CallbackOptions
    ) -> Iterable[metrics.Observation]:
        time_elapsed = time.time() - environment.stats.start_time
        yield metrics.Observation(
            environment.stats.num_requests / time_elapsed
        )

    requests_per_second = otel_meter.create_observable_gauge(
        name="locust.otlp.rps",
        callbacks=[consume_requests_per_second]
    )

class WebsiteOneUser(HttpUser):
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    @task
    def load_test_website_one(self):
        self.client.get("http://swo_ruby_apm_benchmark_on-1:8002/", name="with_apm")
        self.client.get("http://swo_ruby_apm_benchmark_otlp_on-1:8002/", name="with_otlp_apm")
        self.client.get("http://swo_ruby_apm_benchmark_off-2:8002/", name="without_apm")
        self.client.get("http://swo_ruby_apm_benchmark_on_special_liboboe-1:8002/", name="with_special_apm")

    @events.request.add_listener
    def report_response_time(response_time, **kw):

        request_name = kw['name']

        if request_name == 'with_apm':
            http_response_time.record(response_time, attributes={metrics_attribute_name: "with_apm"})
        elif request_name == 'with_otlp_apm':
            http_response_time.record(response_time, attributes={metrics_attribute_name: "with_otlp_apm"})
        elif request_name == 'without_apm':
            http_response_time.record(response_time, attributes={metrics_attribute_name: "without_apm"})
        elif request_name == 'with_special_apm':
            http_response_time.record(response_time, attributes={metrics_attribute_name: "with_special_apm"})
        else:
            print('request_name not found')

