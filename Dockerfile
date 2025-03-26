FROM python:3.10-slim

# 필수 시스템 패키지 + Node.js 설치 (Playwright 의존성)
RUN apt-get update && apt-get install -y \
    wget gnupg curl ca-certificates fonts-liberation libnss3 libxss1 \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 \
    libxrandr2 libgbm1 libxdamage1 libxext6 libxfixes3 libxi6 libglu1-mesa \
    libgtk-3-0 xvfb nodejs npm && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 파이썬 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install --with-deps

# 앱 파일 복사 및 실행 준비
COPY . /app
WORKDIR /app
CMD ["python", "app.py"]
