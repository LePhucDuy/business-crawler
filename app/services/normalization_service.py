import re
from typing import Optional
from datetime import date, datetime
from app.domain.enums import BusinessStatus
import structlog

logger = structlog.get_logger(__name__)

class NormalizationService:
    @staticmethod
    def normalize_tax_code(tax_code: Optional[str]) -> Optional[str]:
        if not tax_code:
            return None
        cleaned = re.sub(r'\D', '', tax_code)
        if len(cleaned) not in (10, 13):
            logger.warning("invalid_tax_code_length", tax_code=tax_code, cleaned=cleaned)
            return None
        return cleaned

    @staticmethod
    def normalize_business_name(name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        return " ".join(name.upper().split())

    @staticmethod
    def normalize_legal_representative(name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        return " ".join(name.upper().split())

    @staticmethod
    def normalize_address(address: Optional[str]) -> Optional[str]:
        if not address:
            return None
        return " ".join(address.split())

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[date]:
        if not date_str:
            return None
        
        date_str = date_str.strip()
        formats = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        logger.warning("unparseable_date", date_str=date_str)
        return None

    @staticmethod
    def normalize_status(status_str: Optional[str]) -> BusinessStatus:
        if not status_str:
            return BusinessStatus.UNKNOWN
            
        status_str = status_str.lower()
        if any(w in status_str for w in ["đang hoạt động", "active"]):
            return BusinessStatus.ACTIVE
        if any(w in status_str for w in ["ngừng hoạt động", "inactive", "đóng cửa"]):
            return BusinessStatus.INACTIVE
        if any(w in status_str for w in ["tạm ngừng", "suspended"]):
            return BusinessStatus.SUSPENDED
            
        return BusinessStatus.UNKNOWN
