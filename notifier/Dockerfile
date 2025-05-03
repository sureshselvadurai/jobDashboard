# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn requests

# Expose the notifier port
EXPOSE 8500

# Start the notifier service
CMD ["uvicorn", "main:app", "--host", "localhost", "--port", "8500"]
