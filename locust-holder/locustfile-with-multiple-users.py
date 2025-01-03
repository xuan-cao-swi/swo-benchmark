from os import environ
import time
from typing import Iterable
from locust import HttpUser, task, between, events

locust_wait_time_l = 0 #int(environ.get("LOCUST_WAIT_TIME_L"))
locust_wait_time_h = 5 #int(environ.get("LOCUST_WAIT_TIME_H"))

class WithAPMUser(HttpUser):
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    host = "http://swo_ruby_apm_benchmark_on-1:8002"
    @task
    def load_test_website_one(self):
        self.client.get("/", name="with_apm")

class WithoutAPMUser(HttpUser):
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    host = "http://swo_ruby_apm_benchmark_off-2:8002"
    @task
    def load_test_website_one(self):
        self.client.get("/", name="without_apm")

class WithOTLPAPMUser(HttpUser):
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    host = "http://swo_ruby_apm_benchmark_otlp_on-1:8002"
    @task
    def load_test_website_one(self):
        self.client.get("/", name="with_otlp_apm")

@events.request.add_listener
def report_response_time(response_time, **kw):
    print(response_time)
    print(kw)
