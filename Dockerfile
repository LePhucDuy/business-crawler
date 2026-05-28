FROM python:3.12-slim

WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết và Brave Browser
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates build-essential \
    && curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list \
    && apt-get update \
    && apt-get install -y brave-browser \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/

# Cài đặt Python dependencies và Playwright
RUN pip install --no-cache-dir hatchling playwright \
    && pip install --no-cache-dir . \
    && playwright install-deps chromium \
    && playwright install chromium

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
