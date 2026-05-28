from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.routes import health, business_lookup
from app.api.response import APIResponse
from app.core.config import settings
from app.core.browser_manager import browser_manager
from app.core.rate_limit import RateLimitMiddleware
import app.crawlers.providers  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    await browser_manager.start()
    yield
    await browser_manager.stop()


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

app.add_middleware(RateLimitMiddleware)


# ─── Global Exception Handlers ────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Chuẩn hóa tất cả HTTPException (401, 403, 404, 500...) về chung 1 format."""
    response = APIResponse.fail(
        message=str(exc.detail),
        code=exc.status_code,
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Chuẩn hóa lỗi validation 422 (sai kiểu dữ liệu, thiếu field...)."""
    errors = exc.errors()
    # Trích xuất thông báo lỗi đầu tiên để làm message chính
    first_error = errors[0] if errors else {}
    field = " -> ".join(str(x) for x in first_error.get("loc", []))
    msg = first_error.get("msg", "Dữ liệu không hợp lệ")
    response = APIResponse.fail(
        message=f"Dữ liệu không hợp lệ: {msg} (field: {field})" if field else msg,
        code=422,
        detail=errors,
    )
    return JSONResponse(status_code=422, content=response.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Bắt tất cả lỗi chưa được xử lý."""
    response = APIResponse.fail(
        message="Lỗi máy chủ nội bộ",
        code=500,
        detail=str(exc),
    )
    return JSONResponse(status_code=500, content=response.model_dump(mode="json"))


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health.router, tags=["Health"])
app.include_router(business_lookup.router, prefix="/api/v1/business", tags=["Business Lookup"])


# ─── 404 catch-all (phải đặt CUỐI CÙNG) ──────────────────────────────────────

from fastapi import Request as _Request  # noqa: E402
from fastapi.responses import JSONResponse as _JSONResponse  # noqa: E402
from fastapi.routing import APIRoute  # noqa: E402

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def not_found_handler(request: _Request):
    response = APIResponse.fail(
        message=f"Endpoint '{request.url.path}' không tồn tại",
        code=404,
    )
    return _JSONResponse(status_code=404, content=response.model_dump(mode="json"))
