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

# Copy the application files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start FastAPI using global Python installation
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
