FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget gnupg curl ca-certificates fonts-liberation libnss3 libxss1 \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 \
    libxrandr2 libgbm1 libxdamage1 libxext6 libxfixes3 libxi6 libglu1-mesa \
    libgtk-3-0 xvfb && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps

COPY . /app
WORKDIR /app
CMD ["python", "app.py"]
