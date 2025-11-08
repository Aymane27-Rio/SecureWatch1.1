FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/webapi
COPY scripts /app/scripts
RUN chmod +x /app/scripts/*.sh || true

# expose
ENV WEBAPI_DB_PATH=/app/data/state/securewatch.db
EXPOSE 8000

CMD ["uvicorn", "webapi.main:app", "--host", "0.0.0.0", "--port", "8000"]