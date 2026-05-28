from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import get_lookup_service
from app.services.business_lookup_service import BusinessLookupService
from app.domain.schemas import BusinessLookupRequest, BusinessLookupResponse

router = APIRouter()

@router.post("/lookup/tax-code", response_model=BusinessLookupResponse)
async def lookup_by_tax_code(
    request: BusinessLookupRequest,
    service: BusinessLookupService = Depends(get_lookup_service)
):
    if not request.tax_code:
        raise HTTPException(status_code=400, detail="tax_code is required")
        
    try:
        return await service.lookup_by_tax_code(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close()
