# Build stage
FROM python:3.10-slim AS builder

WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Final stage
FROM python:3.10-slim

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Copy only the built wheels from the builder stage
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application files
COPY . /app/

# Fix permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]