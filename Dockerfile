# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary dependencies
RUN pip install gunicorn redis
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Environment variables for Celery
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

# Run as non-root user
RUN useradd -m celeryuser
RUN chown -R celeryuser:celeryuser /app
USER celeryuser

CMD ["gunicorn", "--config", "gunicorn_config.py", "service:app"]
