# ==========================================
# STAGE 1: Builder (Tối ưu cài đặt thư viện Python)
# ==========================================
FROM python:3.12-slim as builder

WORKDIR /app

# Cài đặt công cụ build cơ bản cho các thư viện C-extensions (ví dụ: asyncpg, lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Chỉ copy pyproject.toml và README.md trước để tận dụng cache layer của Docker
COPY pyproject.toml README.md /app/

# Build wheels (gói cài đặt) cho tất cả dependencies để tránh phải build lại từ source ở stage sau
RUN pip install --no-cache-dir hatchling \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels . \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels playwright

# ==========================================
# STAGE 2: Final (Môi trường chạy thực tế - Gọn và Cache tốt)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# [LAYER SIÊU NẶNG] - Ít bị thay đổi nhất, đưa lên đầu để Docker cache vĩnh viễn
# Cài đặt các thư viện C++ cơ bản cần thiết (nếu có)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels đã build sẵn từ stage builder sang và cài đặt siêu tốc
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Cài đặt trình duyệt headless Chromium của Playwright và dependencies của nó
# (Layer này cũng ít thay đổi)
RUN playwright install-deps chromium \
    && playwright install chromium

# [LAYER THAY ĐỔI NHIỀU NHẤT] - Copy mã nguồn dự án vào cuối cùng
# Bất cứ khi nào bạn sửa code Python, Docker chỉ mất 1 giây để chạy lại từ bước này
COPY . /app/

# Port mà FastAPI sẽ expose
EXPOSE 8000

# Chạy server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
