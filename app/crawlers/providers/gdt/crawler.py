from app.crawlers.base import BaseBusinessCrawler
from app.domain.enums import ProviderCapability
from app.domain.normalized import BusinessProfileNormalized

class GDTCrawler(BaseBusinessCrawler):
    provider_name = "gdt"
    base_url = "https://tracuunnt.gdt.gov.vn"
    capabilities = [ProviderCapability.TAX_CODE_LOOKUP, ProviderCapability.MANUAL_REVIEW]
    requires_captcha = True  # This will trigger ProviderManualReviewRequired during validate_before_request
    rate_limit_per_minute = 30
    
    async def build_tax_code_url(self, tax_code: str) -> str:
        # Just returning the base search page URL since it requires a captcha to actually search
        return f"{self.base_url}/tcnnt/mstdn.jsp"
        
    async def build_name_search_url(self, name: str) -> str:
        return f"{self.base_url}/tcnnt/mstdn.jsp"
        
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        # GDT requires captcha, so this will rarely be called in automated mode unless ALLOW_MANUAL_CAPTCHA=true
        pass
