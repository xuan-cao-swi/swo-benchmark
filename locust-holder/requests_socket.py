import requests_unixsocket
import json
import time
from multiprocessing import Process

# Define the Unix socket path and container ID
docker_socket_path = "http+unix://%2Fvar%2Frun%2Fdocker.sock"

# Construct the URL for the stats endpoint
apm_off_url     = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_off-2/stats?stream=false"
apm_on_url      = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_on-1/stats?stream=false"
apm_otlp_on_url = f"{docker_socket_path}/containers/swo_ruby_apm_benchmark_otlp_on-1/stats?stream=false"

general_session = requests_unixsocket.Session()

def output_stats(stats, options={}):
    memory_usage_bytes = stats['memory_stats']['usage']
    memory_usage_mb = memory_usage_bytes / (1024 ** 2)

    total_cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
    system_cpu_usage = stats['cpu_stats']['system_cpu_usage']
    cpu_usage_percentage = (total_cpu_usage / system_cpu_usage) * 100

    print(f"{options['container_name']} Memory Usage: {memory_usage_mb:.2f} MB")
    print(f"{options['container_name']} CPU Usage: {cpu_usage_percentage:.6f} %")

# Define the background job
def background_job():
    while True:
        try:
            response = general_session.get(apm_off_url)
            response.raise_for_status()
            stats = response.json()
            output_stats(stats, {'container_name': 'apm_off'})

            response = general_session.get(apm_on_url)
            response.raise_for_status()
            stats = response.json()
            output_stats(stats, {'container_name': 'apm_on'})

            response = general_session.get(apm_otlp_on_url)
            response.raise_for_status()
            stats = response.json()
            output_stats(stats, {'container_name': 'apm_otlp_on'})

            print("   ")

        except requests.RequestException as e:
            print(f"Error fetching stats: {e}")

        time.sleep(10)

# Create the daemon process
daemon_process = Process(target=background_job, daemon=True)

# Start the daemon
daemon_process.start()

print("Main program is running. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)  # Keep the main program alive
except KeyboardInterrupt:
    print("Stopping the program...")



