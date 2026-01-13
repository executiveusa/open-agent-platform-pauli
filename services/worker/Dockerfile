FROM python:3.11-slim

WORKDIR /worker
RUN pip install --no-cache-dir temporalio aiohttp

COPY worker.py /worker/worker.py

CMD ["python", "/worker/worker.py"]
