FROM python:3.11-slim

WORKDIR /app

# Copy repository into image
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r agentic-honeypot/src/requirements.txt

# Use PORT from environment provided by Render
ENV PORT=8000

# Start the FastAPI app (use shell form so $PORT is expanded)
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port $PORT --proxy-headers"
