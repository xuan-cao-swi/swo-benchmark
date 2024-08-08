# test-action-release

## Rails Memory benchmark

### Docker compose with docker stats

Build through docker compose
```
docker compose -f docker-compose-memory-benchmark.yml build
docker compose -f docker-compose-memory-benchmark.yml up
```

check the docker stats
```
docker stats
```

Build single images
```
docker build . -f Dockerfile -t swo_ruby_apm_benchmark:latest --no-cache
```

Start containers
```
docker run  -it --rm --name swo_ruby_apm_benchmark-1 swo_ruby_apm_benchmark:latest /bin/bash
docker run  -it --rm --name swo_ruby_apm_benchmark-1 -v $(pwd)/learn-rails/:/var/app/learn-rails swo_ruby_apm_benchmark:latest /bin/bash
```

### Simulate the request

#### without ab

curl http://swo_ruby_apm_benchmark-1:8002/

curl http://swo_ruby_apm_benchmark-2:8002/ 

curl http://0.0.0.0:8002/

#### with ab

```
ab -n 100000 -c 100 http://swo_ruby_apm_benchmark_on-1:8002/ &
ab -n 100000 -c 100 http://swo_ruby_apm_benchmark_off-2:8002/ &
```

#### simulate the request at same time
```
ab -n 100000 -c 100 http://swo_ruby_apm_benchmark_on-1:8002/ &
P1=$!
ab -n 100000 -c 100 http://swo_ruby_apm_benchmark_off-2:8002/ &
P2=$!
wait $P1 $P2
```

ab -n 100000 -c 100 http://swo_ruby_apm_benchmark-1:8002/ &
P1=$!
ab -n 100000 -c 100 http://swo_ruby_apm_benchmark-2:8002/ &
P2=$!
wait $P1 $P2

```
ab -n 100000 -c 100 http://0.0.0.0:8002/ &
P1=$!
ab -n 100000 -c 100 http://0.0.0.0:8003/ &
P2=$!
wait $P1 $P2
```

### Install AB 

Install components for simulating
apt-get update && apt-get upgrade -y
apt-get install curl apache2-utils -y

Files:
```
docker-compose-memory-benchmark.yml
Dockerfile
```

### Monitor the stats and output graph

start the docker container
run ab_test_infinite.sh
run monitor_docker_stats.py
