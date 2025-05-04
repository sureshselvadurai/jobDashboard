# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements.txt first for caching
COPY requirements.txt /app/requirements.txt

# Install dependencies globally
RUN pip install --no-cache-dir -r requirements.txt

# Ensure `uvicorn` is installed in case it's missing
RUN pip install --no-cache-dir uvicorn

# --- Accept build args and promote them to env variables ---
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG NOTIFIER_URL
ARG FRONTEND_URL

ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV NOTIFIER_URL=${NOTIFIER_URL}
ENV FRONTEND_URL=${FRONTEND_URL}

# Copy the application files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start FastAPI using global Python installation
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
