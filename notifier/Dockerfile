# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn requests

# Accept build-time arguments
ARG SLACK_WEBHOOK_URL

# Promote them to runtime environment variables
ENV SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}

# Expose the notifier port
EXPOSE 8500

# Start the notifier service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8500"]
