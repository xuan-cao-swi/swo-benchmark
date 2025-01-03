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

import requests_unixsocket
import json
from multiprocessing import Process

# Define the Unix socket path and container ID
docker_socket_path = "http+unix://%2Fvar%2Frun%2Fdocker.sock"

# Construct the URL for the stats endpoint
apm_off_url     = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_off-2/stats?stream=false"
apm_on_url      = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_on-1/stats?stream=false"
apm_otlp_on_url = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_otlp_on-1/stats?stream=false"
apm_special_url = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_on_special_liboboe-1/stats?stream=false"

general_session = requests_unixsocket.Session()

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
    metrics_name = 'xuan.ruby.service.response.time' # let default to this one

http_response_time = otel_meter.create_histogram(
    name=metrics_name,
    description="measures the duration of the inbound HTTP request",
    unit="ms")

docker_memory = otel_meter.create_histogram(
    name='xuan.ruby.service.docker.memory',
    description="measures the memory usage",
    unit="mb")

docker_cpu = otel_meter.create_histogram(
    name='xuan.ruby.service.docker.cpu',
    description="measures the cpu usage",
    unit="percentage")

locust_wait_time_l = int(environ.get("LOCUST_WAIT_TIME_L"))
locust_wait_time_h = int(environ.get("LOCUST_WAIT_TIME_H"))
metrics_attribute_name = environ.get("METRICS_ATTRIBUTE_NAME")

def send_stats(stats, options={}):
    memory_usage_bytes = stats['memory_stats']['usage']
    memory_usage_mb = memory_usage_bytes / (1024 ** 2)

    total_cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
    system_cpu_usage = stats['cpu_stats']['system_cpu_usage']
    cpu_usage_percentage = (total_cpu_usage / system_cpu_usage) * 100

    docker_memory.record(round(memory_usage_mb, 2), attributes={metrics_attribute_name: options['container_name']})
    docker_cpu.record(round(cpu_usage_percentage, 4), attributes={metrics_attribute_name: options['container_name']})

# Define the background job
def background_job():
    while True:
        try:
            response = general_session.get(apm_off_url)
            response.raise_for_status()
            stats = response.json()
            send_stats(stats, {'container_name': 'without_apm'})

            response = general_session.get(apm_on_url)
            response.raise_for_status()
            stats = response.json()
            send_stats(stats, {'container_name': 'with_apm'})

            response = general_session.get(apm_otlp_on_url)
            response.raise_for_status()
            stats = response.json()
            send_stats(stats, {'container_name': 'with_otlp_apm'})

            response = general_session.get(apm_special_url)
            response.raise_for_status()
            stats = response.json()
            send_stats(stats, {'container_name': 'with_special_apm'})

        except requests.RequestException as e:
            print(f"Error fetching stats: {e}")

        time.sleep(30)

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

# locust --headless -u 1 --host http://0.0.0.0:8002
# Locust uses requests.Session under the hood for HTTP requests, which enables connection pooling and reuses connections by default.
class WebsiteOneUser(HttpUser):
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    @task
    def load_test_website_one(self):
        self.client.get("http://swo_ruby_apm_benchmark_on-1:8002/", name="with_apm", headers={"Connection": "close"})
        self.client.get("http://swo_ruby_apm_benchmark_otlp_on-1:8002/", name="with_otlp_apm", headers={"Connection": "close"})
        self.client.get("http://swo_ruby_apm_benchmark_off-2:8002/", name="without_apm", headers={"Connection": "close"})
        self.client.get("http://swo_ruby_apm_benchmark_on_special_liboboe-1:8002/", name="with_special_apm", headers={"Connection": "close"})

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

# Create the daemon process
daemon_process = Process(target=background_job, daemon=True)
daemon_process.start()

