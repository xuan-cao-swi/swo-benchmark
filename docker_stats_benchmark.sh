#!/bin/bash


# run locust --headless -u 100 --run-time 1200 --host http://0.0.0.0:8002 # default unit is seconds first, then this file

counter=1
cpu_usage_on=()
mem_usage_on=()
cpu_usage_off=()
mem_usage_off=()

while [ $counter -le 500 ]; do

    echo "Iteration $counter"

    # Get the stats for the two containers
    stats=$(sudo docker stats --no-stream --format "{{.Name}} {{.CPUPerc}} {{.MemUsage}}")

    while IFS= read -r line; do
        container=$(echo $line | awk '{print $1}')

        if [ "$container" = 'swo_ruby_apm_benchmark_on-1' ]; then
            cpu=$(echo $line | awk '{print $2}')
            mem=$(echo $line | awk '{print $3}')
            echo "Container: $container, CPU: $cpu, Memory: $mem"
            cpu_usage_on+=("$cpu")
            mem_usage_on+=("$mem")
        elif [ "$container" = 'swo_ruby_apm_benchmark_off-2' ]; then
            cpu=$(echo $line | awk '{print $2}')
            mem=$(echo $line | awk '{print $3}')
            echo "Container: $container, CPU: $cpu, Memory: $mem"
            cpu_usage_off+=("$cpu")
            mem_usage_off+=("$mem")
        fi
    done <<< "$stats"

    sleep 2
    ((counter++))
done

{
    echo "CPU Usage:"
    for cpu_on in "${cpu_usage_on[@]}"; do
        echo "$cpu_on"
    done

    echo ""

    echo "Memory Usage:"
    for mem_on in "${mem_usage_on[@]}"; do
        echo "$mem_on"
    done
} > docker_stats_on.txt

{
    echo "CPU Usage:"
    for cpu_off in "${cpu_usage_off[@]}"; do
        echo "$cpu_off"
    done

    echo ""

    echo "Memory Usage:"
    for mem_off in "${mem_usage_off[@]}"; do
        echo "$mem_off"
    done
} > docker_stats_off.txt
