FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure the upload directory exists
RUN mkdir -p data/compliance_policies