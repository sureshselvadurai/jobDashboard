# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy frontend files into the container
COPY . /app

# Expose the frontend port
EXPOSE 5500

# Run the Python server
CMD ["python", "server.py"]
