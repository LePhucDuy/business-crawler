from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.normalized import BusinessProfileNormalized
from app.domain.enums import ProviderResultStatus

class ProviderResult(BaseModel):
    provider_name: str
    success: bool
    status: ProviderResultStatus
    profile: Optional[BusinessProfileNormalized] = None
    error_message: Optional[str] = None
    source_url: Optional[str] = None
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int = 0
    manual_review_url: Optional[str] = None
    manual_review_reason: Optional[str] = None
    
    @classmethod
    def not_supported(cls, provider_name: str):
        return cls(provider_name=provider_name, success=False, status=ProviderResultStatus.NOT_SUPPORTED)
        
    @classmethod
    def captcha_detected(cls, provider_name: str, url: str = None):
        return cls(provider_name=provider_name, success=False, status=ProviderResultStatus.CAPTCHA_DETECTED, source_url=url)
        
    @classmethod
    def success_result(cls, provider_name: str, profile: BusinessProfileNormalized, source_url: str, duration_ms: int = 0):
        return cls(provider_name=provider_name, success=True, status=ProviderResultStatus.SUCCESS, profile=profile, source_url=source_url, duration_ms=duration_ms)

class BusinessMergeResult(BaseModel):
    final_profile: BusinessProfileNormalized
    provider_results: List[ProviderResult]
    conflicts: List[Dict[str, Any]] = []
    needs_manual_review: bool = False
    confidence_score: float = 0.0

class BusinessLookupRequest(BaseModel):
    tax_code: Optional[str] = None
    name: Optional[str] = None
    force_refresh: bool = False
    providers: Optional[List[str]] = None
    limit: int = 10

class BusinessLookupResponse(BaseModel):
    success: bool
    data: Optional[BusinessProfileNormalized] = None
    provider_results: List[ProviderResult] = []
    needs_manual_review: bool = False
    conflicts: List[Dict[str, Any]] = []
