from fastapi import APIRouter
from app.api.response import APIResponse

router = APIRouter()

@router.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse.ok(data={"status": "ok"}, message="Service đang hoạt động bình thường")
