from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_lookup_service
from app.api.response import APIResponse
from app.services.business_lookup_service import BusinessLookupService
from app.domain.schemas import BusinessLookupRequest

router = APIRouter()

@router.post("/lookup/tax-code", response_model=APIResponse)
async def lookup_by_tax_code(
    request: BusinessLookupRequest,
    service: BusinessLookupService = Depends(get_lookup_service)
):
    if not request.tax_code:
        return APIResponse.fail(message="tax_code là bắt buộc", code=400)

    try:
        result = await service.lookup_by_tax_code(request)
        if result.success:
            return APIResponse.ok(
                data=result.model_dump(mode="json"),
                message="Tra cứu thành công"
            )
        else:
            return APIResponse.fail(
                message="Không tìm thấy thông tin doanh nghiệp",
                code=404
            )
    except Exception as e:
        return APIResponse.fail(message="Lỗi hệ thống", code=500, detail=str(e))
    finally:
        await service.close()
