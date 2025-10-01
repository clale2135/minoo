# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set environment variables
ENV PORT=8080

# Expose port
EXPOSE 8080

# Simple command to run streamlit with debug output
CMD streamlit run --server.port $PORT --server.address 0.0.0.0 app.py --logger.level=info