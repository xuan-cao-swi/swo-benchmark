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

import requests_unixsocket
import json
from multiprocessing import Process

# Define the Unix socket path and container ID
docker_socket_path = "http+unix://%2Fvar%2Frun%2Fdocker.sock"

# Construct the URL for the stats endpoint
# "http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/swo_ruby_apm_benchmark_off-2/stats?stream=false"
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

docker_memory = otel_meter.create_histogram(
    name='xuan.ruby.service.docker.memory',
    description="measures the memory usage",
    unit="mb")

docker_cpu = otel_meter.create_histogram(
    name='xuan.ruby.service.docker.cpu',
    description="measures the cpu usage",
    unit="percentage")

metrics_attribute_name = environ.get("METRICS_ATTRIBUTE_NAME")
time_sleep_on_daemon = environ.get("TIME_SLEEP_ON_DAEMON", 10)

# stats['cpu_stats']:
# {'cpu_usage': {'total_usage': 10711298000, 'usage_in_kernelmode': 2091244000, 'usage_in_usermode': 8620053000}, 'system_cpu_usage': 106497330000000, 'online_cpus': 16, 'throttling_data': {'periods': 874, 'throttled_periods': 6, 'throttled_time': 61023000}}
def send_stats(stats, options={}):
    memory_usage_bytes = stats['memory_stats']['usage']
    memory_usage_mb = memory_usage_bytes / (1024 ** 2)

    total_cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
    system_cpu_usage = stats['cpu_stats']['system_cpu_usage']
    cpu_usage_percentage = (total_cpu_usage / system_cpu_usage) * 100

    docker_stats_result = f"memory_usage_mb: {memory_usage_mb}; total_cpu_usage: {total_cpu_usage}; system_cpu_usage: {system_cpu_usage};"

    # docker_memory.record(round(memory_usage_mb, 2), attributes={metrics_attribute_name: options['container_name']})
    # docker_cpu.record(round(cpu_usage_percentage, 4), attributes={metrics_attribute_name: options['container_name']})

    return docker_stats_result

# Define the background job
def background_job(url, options):
    while True:
        try:
            response = general_session.get(url)
            response.raise_for_status()
            stats = response.json()
            send_stats(stats, options)

        except requests.RequestException as e:
            print(f"Error fetching stats: {e}")

        time.sleep(time_sleep_on_daemon)

# Create the daemon process
daemon_process1 = Process(target=background_job, args=(apm_off_url, {'container_name': 'without_apm'}), daemon=True)
daemon_process2 = Process(target=background_job, args=(apm_on_url, {'container_name': 'with_apm'}), daemon=True)
daemon_process3 = Process(target=background_job, args=(apm_otlp_on_url, {'container_name': 'with_otlp_apm'}), daemon=True)
daemon_process4 = Process(target=background_job, args=(apm_special_url, {'container_name': 'with_special_apm'}), daemon=True)

daemon_process1.start()
daemon_process2.start()
daemon_process3.start()
daemon_process4.start()

# nohup python3 docker_stats_monitor.py > output.log 2>&1 &



