

## Build/Run the image

```sh
docker build . -t locust_app_holder:latest --no-cache
docker run  -it --rm --name locust_app_holder locust_app_holder
```