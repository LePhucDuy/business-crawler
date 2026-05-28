from app.crawlers.base import BaseBusinessCrawler
from app.domain.enums import ProviderCapability
from app.domain.normalized import BusinessProfileNormalized
from app.crawlers.providers.vietqr.parser import VietQRParser

class VietQRCrawler(BaseBusinessCrawler):
    provider_name = "vietqr"
    base_url = "https://api.vietqr.io"
    capabilities = [ProviderCapability.TAX_CODE_LOOKUP]
    requires_captcha = False
    rate_limit_per_minute = 120  # API usually has higher limits
    
    def __init__(self, http_client):
        super().__init__(http_client)
        self.parser = VietQRParser()
        
    async def build_tax_code_url(self, tax_code: str) -> str:
        return f"{self.base_url}/v2/business/{tax_code}"
        
    async def build_name_search_url(self, name: str) -> str:
        raise NotImplementedError("VietQR provider only supports tax_code lookup")
        
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        return self.parser.parse_detail_page(html, source_url)
