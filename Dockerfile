FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxrandr2 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 \
    libasound2 libgtk-3-0 libxdamage1 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN playwright install --with-deps

# Copy app files
COPY . .

# Expose port
EXPOSE 10000

# Start command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]