from app.crawlers.base import BaseBusinessCrawler
from app.domain.enums import ProviderCapability
from app.domain.normalized import BusinessProfileNormalized

class GenericHtmlCrawler(BaseBusinessCrawler):
    """
    A generic crawler that can be configured via JSON/YAML for simple websites.
    """
    provider_name = "generic"
    base_url = ""
    capabilities = [ProviderCapability.TAX_CODE_LOOKUP]
    
    def __init__(self, http_client, config_dict: dict):
        super().__init__(http_client)
        self.provider_name = config_dict.get("provider_name", "generic")
        self.base_url = config_dict.get("base_url", "")
        self.config_dict = config_dict
        
    async def build_tax_code_url(self, tax_code: str) -> str:
        pattern = self.config_dict.get("detail_url_pattern", "")
        return pattern.replace("{tax_code}", tax_code)
        
    async def build_name_search_url(self, name: str) -> str:
        raise NotImplementedError()
        
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        selectors = self.config_dict.get("selectors", {})
        
        def extract(key):
            sel = selectors.get(key)
            if sel:
                el = soup.select_one(sel)
                if el:
                    return el.get_text(strip=True)
            return None
            
        from app.services.normalization_service import NormalizationService
        from datetime import datetime
        
        tax_code = extract("tax_code")
        business_name = extract("business_name")
        address = extract("address")
        representative = extract("legal_representative")
        status = extract("status")
        
        return BusinessProfileNormalized(
            tax_code=NormalizationService.normalize_tax_code(tax_code),
            business_name=business_name,
            normalized_business_name=NormalizationService.normalize_business_name(business_name),
            address=address,
            normalized_address=NormalizationService.normalize_address(address),
            legal_representative=representative,
            normalized_legal_representative=NormalizationService.normalize_legal_representative(representative),
            status=NormalizationService.normalize_status(status),
            source_name=self.provider_name,
            source_url=source_url,
            crawled_at=datetime.utcnow()
        )
