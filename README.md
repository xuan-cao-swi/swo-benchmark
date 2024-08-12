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
apt-get install python3-pip
apt-get install python3.12-venv

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
