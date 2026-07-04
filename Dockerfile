FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY app/sync.py /app/sync.py

CMD ["python", "-u", "/app/sync.py"]
