from locust import HttpUser, task, between

class WebsiteOneUser(HttpUser):
    wait_time = between(1, 5)
    @task
    def load_test_website_one(self):
        self.client.get("http://0.0.0.0:8002/", name="with_apm")
        self.client.get("http://0.0.0.0:8003/", name="without_apm")

# https://docs.locust.io/en/stable/running-without-web-ui.html
# locust --headless -u 100 --run-time 60 --host http://0.0.0.0:8002 # default unit is seconds

# On multiple host
# https://github.com/locustio/locust/issues/150