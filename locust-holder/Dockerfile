# Use the official Python 3.12 image from the Docker Hub
FROM python:3.12

COPY requirements.txt .
COPY locustfile.py .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# CMD ["tail", "-f", "/dev/null"]
CMD ["locust", "--headless", "-u", "1", "--host", "http://0.0.0.0:8002"]
# locust --headless -u 1 --host http://0.0.0.0:8002
