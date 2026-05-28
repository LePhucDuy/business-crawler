import json
from datetime import datetime
from app.crawlers.parsers.base_parser import BaseBusinessParser
from app.domain.normalized import BusinessProfileNormalized
from app.services.normalization_service import NormalizationService
import structlog

logger = structlog.get_logger(__name__)

class VietQRParser(BaseBusinessParser):
    provider_name = "vietqr"

    def parse_detail_page(self, html: str, source_url: str) -> BusinessProfileNormalized:
        try:
            payload = json.loads(html)
        except json.JSONDecodeError:
            logger.error("vietqr_parse_error", error="Invalid JSON")
            return BusinessProfileNormalized(
                source_name=self.provider_name,
                source_url=source_url,
                crawled_at=datetime.utcnow()
            )

        # Check API status
        if payload.get("code") != "00" or not payload.get("data"):
            logger.info("vietqr_not_found", code=payload.get("code"), desc=payload.get("desc"))
            return BusinessProfileNormalized(
                source_name=self.provider_name,
                source_url=source_url,
                crawled_at=datetime.utcnow()
            )

        data = payload["data"]
        
        tax_code = data.get("id")
        business_name = data.get("name")
        international_name = data.get("internationalName")
        short_name = data.get("shortName")
        address = data.get("address")
        status = data.get("status")

        profile = BusinessProfileNormalized(
            tax_code=NormalizationService.normalize_tax_code(tax_code),
            business_name=business_name,
            normalized_business_name=NormalizationService.normalize_business_name(business_name),
            international_name=international_name,
            short_name=short_name,
            address=address,
            normalized_address=NormalizationService.normalize_address(address),
            legal_representative=None,
            normalized_legal_representative=None,
            status=NormalizationService.normalize_status(status),
            source_name=self.provider_name,
            source_url=source_url,
            crawled_at=datetime.utcnow()
        )
        return profile
