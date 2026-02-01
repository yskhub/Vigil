FROM python:3.11-slim

WORKDIR /app

# system deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc curl && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy source
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Healthcheck uses the readiness endpoint
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 CMD curl -f http://127.0.0.1:8000/ready || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
FROM python:3.11-slim

WORKDIR /app/agentic-honeypot

# Copy repository into image root
COPY . /app

# Install dependencies (relative to working dir)
RUN pip install --no-cache-dir -r src/requirements.txt

# Use PORT from environment provided by Render
ENV PORT=8000

# Start the FastAPI app from the agentic-honeypot folder
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port $PORT --proxy-headers"
