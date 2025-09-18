FROM python:3.11-slim

# Creating the app directory
WORKDIR /app

# installing requiements
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the rest of the application code
COPY . .

# execution rights to scripts
RUN chmod +x scripts/*.sh modules/*.sh

# Default command: run full sweep
CMD ["bash", "scripts/securewatch.sh"]
