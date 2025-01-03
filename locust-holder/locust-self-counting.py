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
exporter =  OTLPMetricExporter(
    endpoint="otel.collector.na-01.st-ssp.solarwinds.com:443",
    insecure=False,
    headers={
        "authorization": f"Bearer {api_token}"
    }
)

reader = PeriodicExportingMetricReader(
    exporter,
    export_interval_millis=5_000,
)

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[reader],
)

metrics.set_meter_provider(meter_provider)
otel_meter = meter_provider.get_meter("benchmark-always-sample")

metrics_name = environ.get("CUSTOM_METRICS_NAME")
if metrics_name == None or metrics_name == '':
    metrics_name = 'xuan.ruby.self.counting.response.time.' # let default to this one

http_response_time = otel_meter.create_histogram(
    name=metrics_name,
    description="measures the duration of the inbound HTTP request",
    unit="ms")

locust_wait_time_l = 10 # int(environ.get("LOCUST_WAIT_TIME_L"))
locust_wait_time_h = 20 # int(environ.get("LOCUST_WAIT_TIME_H"))
metrics_attribute_name = 'xuan-test' # environ.get("METRICS_ATTRIBUTE_NAME")

request = {'with_apm': {'request_count' : 0, 'request_time' : 0 },
           'with_otlp_apm': {'request_count' : 0, 'request_time' : 0 },
           'without_apm': {'request_count' : 0, 'request_time' : 0 }
          }

class WebsiteOneUser(HttpUser):
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    @task
    def load_test_website_one(self):
        self.client.get("http://swo_ruby_apm_benchmark_on-1:8002/", name="with_apm")
        self.client.get("http://swo_ruby_apm_benchmark_otlp_on-1:8002/", name="with_otlp_apm")
        self.client.get("http://swo_ruby_apm_benchmark_off-2:8002/", name="without_apm")

# this will be called three times if there are three get
@events.request.add_listener
def report_response_time(response_time, **kw):
    request_name = kw['name']
    request[request_name]['request_count'] += 1
    request[request_name]['request_time'] += int(response_time)
    avg = int(request[request_name]['request_time'] / request[request_name]['request_count'])
    http_response_time.record(avg, attributes={metrics_attribute_name: request_name})
