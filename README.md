# Business Crawler API (eKYB Vietnam)

Hệ thống tra cứu, thu thập và chuẩn hóa dữ liệu doanh nghiệp Việt Nam tự động (eKYB - Electronic Know Your Business) dựa trên Mã số thuế hoặc Tên doanh nghiệp. Hệ thống được thiết kế với cơ chế chống block nâng cao và tự động dự phòng giữa nhiều nguồn dữ liệu khác nhau.

## 🌟 Tính năng nổi bật

- **Anti-Bot Bypass (Bypass Cloudflare):** Sử dụng Playwright giả lập trình duyệt (Chromium/Brave) kết hợp các tham số tàng hình để vượt qua tường lửa Cloudflare của các trang tra cứu.
- **Sequential Fallback Strategy:** Cơ chế "chuyển nguồn thông minh". Nếu nguồn dữ liệu 1 (ví dụ: `masothue.com`) bị sập hoặc không có dữ liệu, hệ thống tự động gọi sang nguồn thứ 2, thứ 3... (ví dụ: `gdt`, `hosocongty`).
- **Search Engine Fallback (DuckDuckGo):** Tích hợp tra cứu trung gian qua trình duyệt thuần HTML của DuckDuckGo để tìm link trực tiếp của doanh nghiệp khi các thanh công cụ tìm kiếm nội bộ của trang web mục tiêu bị lỗi.
- **Smart Caching:** Dữ liệu sau khi cào sẽ được lưu vào Database (PostgreSQL/SQLite). Các yêu cầu trùng lặp trong thời gian ngắn sẽ được trả về từ Cache (thời gian sống của Cache thay đổi tùy vào trạng thái hoạt động của doanh nghiệp).
- **Dockerized (Multi-stage Build):** Đóng gói hoàn chỉnh bằng Docker với kỹ thuật multi-stage build giúp tối ưu thời gian build và triển khai lên server cực kì nhanh chóng.

## 🛠 Công nghệ sử dụng

- **Core:** Python 3.11+, FastAPI (Sắp tích hợp)
- **Database:** SQLAlchemy (Async), PostgreSQL / SQLite, Alembic (Migrations)
- **Crawler:** Playwright (Async), HTTPX, BeautifulSoup4, LXML
- **Fuzzy Matching:** RapidFuzz (so khớp tên doanh nghiệp tự động)
- **Deployment:** Docker, Docker Compose

---

## 🚀 Hướng dẫn cài đặt & Chạy trên máy cá nhân (Local)

### 1. Yêu cầu hệ thống
- Python 3.11 hoặc cao hơn
- Cài đặt sẵn `make` (khuyến nghị)

### 2. Cài đặt thư viện
```bash
# Clone dự án
git clone https://github.com/LePhucDuy/business-crawler.git
cd business-crawler

# Cài đặt các thư viện Python (dùng môi trường ảo)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Cài đặt Playwright (Trình duyệt nội bộ)
Hệ thống sử dụng Chromium của Playwright để làm tác vụ cào dữ liệu:
```bash
playwright install chromium
# Nếu dùng Linux, chạy thêm lệnh sau để cài thư viện C++ cần thiết:
playwright install-deps chromium
```

### 4. Cấu hình biến môi trường
```bash
cp .env.example .env
```
*Lưu ý: Nếu bạn sử dụng trình duyệt Brave có sẵn trong máy tính cá nhân, hãy trỏ đường dẫn tới biến `BRAVE_EXECUTABLE_PATH` trong file `.env`. Nếu chạy trên Server, hãy để trống biến đó.*

### 5. Khởi tạo Database
```bash
# Áp dụng các bảng vào Database
alembic upgrade head
```

### 6. Chạy thử qua Command Line (CLI)
```bash
# Tra cứu 1 doanh nghiệp bằng mã số thuế
python3 -m app.cli.lookup --tax-code 0319570124
```

---

## 🐳 Triển khai lên Server bằng Docker

Dự án đã được cấu hình sẵn `Dockerfile` siêu tối ưu (chứa sẵn Chromium) và `docker-compose.yml`.

```bash
# Build và chạy ngầm dự án
docker-compose up -d --build

# Xem log chạy của ứng dụng
docker-compose logs -f
```

---

## ⚙️ Cấu hình chiến lược thu thập (Crawl Strategy)

Trong file `.env`, bạn có thể can thiệp sâu vào cách hệ thống hoạt động:

```env
# DANH SÁCH NGUỒN (Xếp theo thứ tự ưu tiên)
ENABLED_PROVIDERS=masothue,gdt

# CHIẾN LƯỢC: 
# "fallback": Nếu masothue có dữ liệu -> Dừng. Nếu thất bại -> Chạy tiếp gdt. (Tiết kiệm tài nguyên)
# "parallel": Chạy song song tất cả các nguồn cùng lúc và tự gộp dữ liệu. (Đầy đủ nhưng tốn tài nguyên)
CRAWL_STRATEGY=fallback
```

---

## 🔌 Tài liệu API (API Reference) cho tích hợp eKYB

Hệ thống cung cấp RESTful API qua cổng `8000`. Bạn có thể truy cập `http://localhost:8000/docs` (Swagger UI) để xem trực quan định dạng JSON.

### 1. Tra cứu doanh nghiệp bằng Mã số thuế

**Endpoint:** `POST /api/v1/business/lookup/tax-code`  
**Content-Type:** `application/json`

**📌 Request Body:**
```json
{
  "tax_code": "0319570124", 
  "force_refresh": false,   
  "providers": ["masothue", "gdt"], 
  "limit": 10
}
```
*Ghi chú tham số:*
- `tax_code` *(bắt buộc)*: Mã số thuế cần tra cứu (VD: "0319570124").
- `force_refresh` *(tùy chọn)*: Mặc định là `true` (Hệ thống luôn tự động cào dữ liệu mới nhất từ nguồn web và bỏ qua Cache để đảm bảo eKYB chính xác nhất). Nếu bạn muốn dùng dữ liệu cũ trong Database cho nhanh, hãy truyền `false`.
- `providers` *(tùy chọn)*: Chỉ định danh sách crawler sẽ dùng cho request này. Nếu bỏ trống, sẽ dùng mặc định theo `ENABLED_PROVIDERS` trong file `.env`.

**📌 Response (Thành công - HTTP 200):**
```json
{
  "success": true,
  "data": {
    "tax_code": "0319570124",
    "business_code": null,
    "business_name": "CÔNG TY TNHH COCO SEA",
    "normalized_business_name": "CÔNG TY TNHH COCO SEA",
    "legal_representative": "NGUYỄN THỊ CẨM TIÊN",
    "normalized_legal_representative": "NGUYỄN THỊ CẨM TIÊN",
    "address": "991B Tân Kỳ Tân Quý, Phường Bình Hưng Hòa, Thành phố Hồ Chí Minh, Việt Nam",
    "status": "ACTIVE",
    "issued_date": "2023-11-20",
    "source_name": "masothue",
    "source_url": "https://masothue.com/0319570124-cong-ty-tnhh-coco-sea",
    "confidence_score": 100.0
  },
  "needs_manual_review": false,
  "conflicts": [],
  "provider_results": [
      // Chi tiết log thu thập từ từng Provider
  ]
}
```

**📌 Response (Lỗi - HTTP 4xx/5xx):**
```json
{
  "detail": "tax_code is required"
}
```

### 💡 Gợi ý tích hợp vào hệ thống eKYB nội bộ:
Khi gọi sang API này, Microservice eKYB của bạn nên xử lý theo logic sau:
1. Gọi API lấy thông tin: Bắn `tax_code` của khách hàng vào đây.
2. Kiểm tra `success == true` và `data != null`.
3. So khớp Tên doanh nghiệp: Lấy `data.business_name` trả về so sánh độ trùng lặp (Fuzzy String Matching) với tên mà đối tác đăng ký. Nếu trùng khớp trên 90% thì duyệt.
4. Kiểm tra sức khỏe doanh nghiệp: Đảm bảo `data.status == "ACTIVE"` (Đang hoạt động) thay vì `LOCKED` (Khóa/Giải thể).
5. (Nâng cao): Nếu `needs_manual_review == true`, đánh dấu hồ sơ này cần nhân viên Ops (Con người) vào kiểm duyệt thủ công do hệ thống bị captcha hoặc 2 nguồn trả về data trái ngược nhau (`conflicts`).

---
*Dự án đang trong quá trình phát triển (WIP).*
