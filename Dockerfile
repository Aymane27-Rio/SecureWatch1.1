# Minimal Dockerfile for running the exporter only (optional)
FROM python:3.11-slim
WORKDIR /app
COPY python/requirements.txt /app/python/requirements.txt
RUN pip install -r /app/python/requirements.txt
COPY python /app/python
COPY data /app/data
EXPOSE 9109
CMD ["python", "/app/python/exporters/securewatch_exporter.py"]
