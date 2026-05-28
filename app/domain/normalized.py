from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class BusinessProfileNormalized(BaseModel):
    tax_code: Optional[str] = None
    business_code: Optional[str] = None
    business_name: Optional[str] = None
    normalized_business_name: Optional[str] = None
    international_name: Optional[str] = None
    short_name: Optional[str] = None
    legal_representative: Optional[str] = None
    normalized_legal_representative: Optional[str] = None
    address: Optional[str] = None
    normalized_address: Optional[str] = None
    tax_authority: Optional[str] = None
    status: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    issued_date: Optional[date] = None
    started_date: Optional[date] = None
    updated_date: Optional[date] = None
    
    source_name: str
    source_url: Optional[str] = None
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: Optional[float] = None
    raw_payload: Optional[Dict[str, Any]] = None
