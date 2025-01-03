from os import environ
import time
from typing import Iterable
from locust import HttpUser, task, between, events

class WebsiteOneUser(HttpUser):
    locust_wait_time_l = int(environ.get("LOCUST_WAIT_TIME_L"))
    locust_wait_time_h = int(environ.get("LOCUST_WAIT_TIME_H"))
    wait_time = between(locust_wait_time_l, locust_wait_time_h)
    @task
    def load_test_website_one(self):
        self.client.get("http://swo_ruby_apm_benchmark_on-1:8002/", name="with_apm")
        self.client.get("http://swo_ruby_apm_benchmark_otlp_on-1:8002/", name="with_otlp_apm")
        self.client.get("http://swo_ruby_apm_benchmark_off-2:8002/", name="without_apm")
