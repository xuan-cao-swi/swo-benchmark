import matplotlib.pyplot as plt
import re

# Function to parse the file
def parse_usage_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    cpu_usage = []
    memory_usage = []

    # Extract CPU and Memory usage values
    for line in lines:
        if 'CPU Usage' in line:
            continue
        elif 'Memory Usage' in line:
            continue
        elif '%' in line:
            cpu_usage.append(float(line.strip().replace('%', '')))
        elif 'MiB' in line:
            memory_usage.append(float(line.strip().replace('MiB', '')))

    return cpu_usage, memory_usage

# Parse the file
cpu_usage_on, memory_usage_on = parse_usage_file('docker_stats_on.txt')
cpu_usage_off, memory_usage_off = parse_usage_file('docker_stats_off.txt')


# Generate an example time index
half = int(len(cpu_usage_on)/2)
cpu_usage_on = cpu_usage_on[0:half]
memory_usage_on = memory_usage_on[0:half]
cpu_usage_off = cpu_usage_off[0:half]
memory_usage_off = memory_usage_off[0:half]

time = range(len(cpu_usage_on))

# Plot CPU Usage
plt.figure(figsize=(14, 7))

# Create the plot
plt.plot(time, cpu_usage_on, label='APM ON', marker='o')
plt.plot(time, cpu_usage_off, label='APM OFF', marker='x')

# Add titles and labels
plt.title('CPU Usage')
plt.xlabel('Time')
plt.ylabel('%')

# Add a legend
plt.legend()
plt.tight_layout()
plt.savefig('cpu_compare.png')


# Plot Memory Usage
plt.figure(figsize=(14, 7))
plt.plot(time, memory_usage_on, label='APM ON', marker='o')
plt.plot(time, memory_usage_off, label='APM OFF', marker='x')

# Add titles and labels
plt.title('Memory Usage')
plt.xlabel('Time')
plt.ylabel('MiB')

# Add a legend
plt.legend()
plt.tight_layout()
plt.savefig('memory_compare.png')
