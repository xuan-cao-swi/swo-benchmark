## Build/Run the image

```sh
docker build . -t locust_app_holder:latest --no-cache
docker run  -it --rm --name locust_app_holder locust_app_holder
```

## locustfile

Locust doesn’t have a built-in function specifically named report_response_time,
but you can track and report response times using Locust’s event hooks and the request event.
Here’s an example of how you can log response times:

https://docs.locust.io/en/stable/running-without-web-ui.html
locust --headless -u 100 --run-time 60 --host http://0.0.0.0:8002 # default unit is seconds
locust --headless -u 100 --host http://0.0.0.0:8002

On multiple host
https://github.com/locustio/locust/issues/150


## Get other docker stats

curl --unix-socket /var/run/docker.sock http://host.docker.internal/containers/174bcbe44471/stats?stream=false
