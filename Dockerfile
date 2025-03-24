FROM python:3.10-slim

WORKDIR /app

# Playwright가 설치된 브라우저를 런타임에 직접 참조하도록 설정
ENV PLAYWRIGHT_BROWSERS_PATH=0

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxrandr2 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 \
    libasound2 libgtk-3-0 libxdamage1 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 브라우저 직접 설치 (Playwright가 사용하는 실행 경로 내부에)
RUN playwright install chromium

COPY . .

EXPOSE 10000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
