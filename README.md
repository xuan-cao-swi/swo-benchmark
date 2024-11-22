# SWO Benchmark

## Run AB Testing

You can do it either in container `benchmark-app-holder` or host machine, but the ip address need to change accordingly

Install AB
```bash
apt-get update && apt-get upgrade -y
apt-get install curl apache2-utils -y
ab -V # check if ab is installed
```

Run AB script (on host machine)
```sh
ab -n 10000 -c 100 http://0.0.0.0:8002/ &
P1=$!
ab -n 10000 -c 100 http://0.0.0.0:8003/ &
P2=$!
wait $P1 $P2
```

Run AB script (on docker container)
```sh
ab -n 1 -c 1 http://swo_ruby_apm_benchmark_on-1:8002/ &
P1=$!
ab -n 1 -c 1 http://swo_ruby_apm_benchmark_off-2:8002/ &
P2=$!
wait $P1 $P2
```

## Run Locust Testing

It's recommended to run in host machine because you can see the graph

Install Locust
```sh
apt-get update && apt-get install python3-pip python3.12-venv vim

# create python virtual env
python3 -m venv locustenv
# activate virtual env
source locustenv/bin/activate

pip3 install locust
```

Create locustfile.py for host machine
```python
from locust import HttpUser, task, between

class WebsiteOneUser(HttpUser):
    wait_time = between(1, 5)
    @task
    def load_test_website_one(self):
        self.client.get("http://0.0.0.0:8002/", name="with_apm")
        self.client.get("http://0.0.0.0:8004/", name="with_otlp_apm")
        self.client.get("http://0.0.0.0:8003/", name="without_apm")
```

Create locustfile.py for container machine
```python
from locust import HttpUser, task, between

class WebsiteOneUser(HttpUser):
    wait_time = between(1, 5)
    @task
    def load_test_website_one(self):
        self.client.get("http://swo_ruby_apm_benchmark_on-1:8002/", name="with_apm")
        self.client.get("http://swo_ruby_apm_benchmark_otlp_on-1:8002/", name="with_otlp_apm")
        self.client.get("http://swo_ruby_apm_benchmark_off-2:8002/", name="without_apm")
```

Run the locust without web UI
```sh
locust --headless -u 100 --run-time 60 --host http://0.0.0.0:8002 # default unit is seconds
```

Run the locust with web UI
```sh
locust
```

## SolarWinds Docker integration

### Setup:
Connect ec2 to solarwinds: https://documentation.solarwinds.com/en/success_center/observability/content/configure/configure-host.htm

Setup docker monitor: https://documentation.solarwinds.com/en/success_center/observability/content/configure/configure-docker.htm

benchmark dashboard: https://my.na-01.st-ssp.solarwinds.com/205939959869206528/entities/docker-daemons/e-1791561768517537792/overview?duration=3600

Check if the solarwinds service is up:
```
service uamsclient status
```


## locustfile_with_metrics.py

SERVICE_NAME
metircs_endpoint
