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
