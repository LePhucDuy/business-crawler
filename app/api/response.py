from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime, timezone

T = TypeVar("T")


class ResponseMeta(BaseModel):
    timestamp: str
    version: str = "1.0"


class APIResponse(BaseModel):
    """
    Unified response envelope cho toàn bộ API.

    Thành công:
        {"success": true, "message": "...", "data": {...}, "error": null, "meta": {...}}

    Thất bại:
        {"success": false, "message": "...", "data": null, "error": {"code": ..., "detail": "..."}, "meta": {...}}
    """
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[dict] = None
    meta: ResponseMeta

    @classmethod
    def ok(cls, data: Any = None, message: str = "Success") -> "APIResponse":
        return cls(
            success=True,
            message=message,
            data=data,
            error=None,
            meta=ResponseMeta(timestamp=datetime.now(timezone.utc).isoformat()),
        )

    @classmethod
    def fail(cls, message: str, code: int = 400, detail: Any = None) -> "APIResponse":
        return cls(
            success=False,
            message=message,
            data=None,
            error={"code": code, "detail": detail or message},
            meta=ResponseMeta(timestamp=datetime.now(timezone.utc).isoformat()),
        )
