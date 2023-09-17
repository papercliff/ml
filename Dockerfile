# Dockerfile
FROM python:3.9-slim AS builder

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create virtualenv and upgrade pip
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip==23.1.2

# Install dependencies
COPY requirements.txt requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Install Gunicorn into virtualenv
RUN /opt/venv/bin/pip install gunicorn

# Copy project
COPY . .

# Second stage: set up the runtime
FROM python:3.9-slim

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy virtualenv and project from builder stage
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app .

EXPOSE 5000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
