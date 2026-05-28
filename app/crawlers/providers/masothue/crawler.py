from app.crawlers.browser import BrowserBusinessCrawler
from app.domain.enums import ProviderCapability
from app.domain.normalized import BusinessProfileNormalized
from app.crawlers.providers.masothue.parser import MasothueParser
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from app.domain.schemas import ProviderResult
import structlog
import time

logger = structlog.get_logger(__name__)

class MasothueCrawler(BrowserBusinessCrawler):
    provider_name = "masothue"
    base_url = "https://masothue.com"
    capabilities = [ProviderCapability.TAX_CODE_LOOKUP, ProviderCapability.NAME_LOOKUP]
    requires_captcha = False
    rate_limit_per_minute = 20
    
    def __init__(self, http_client):
        super().__init__(http_client)
        self.parser = MasothueParser()
    
    async def build_tax_code_url(self, tax_code: str) -> str:
        return f"{self.base_url}/Search/?q={tax_code}"
        
    async def build_name_search_url(self, name: str) -> str:
        return f"{self.base_url}/Search/?q={name}"
        
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        return self.parser.parse_detail_page(html, source_url)

    async def lookup_by_tax_code(self, tax_code: str) -> ProviderResult:
        start_time = time.time()
        result = await super().lookup_by_tax_code(tax_code)
        
        # If successfully crawled but not found, use DuckDuckGo fallback
        if result.success and result.profile and not result.profile.tax_code:
            logger.info("masothue_search_failed_trying_fallback", tax_code=tax_code)
            try:
                search_url = f"https://html.duckduckgo.com/html/?q=site:masothue.com+{tax_code}"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                response = await self.http_client.get(search_url, headers=headers, follow_redirects=True, timeout=10)
                html = response.text
                
                soup = BeautifulSoup(html, "html.parser")
                links = soup.find_all("a", class_="result__url", href=True)
                logger.info("duckduckgo_links_found", count=len(links))
                
                target_url = None
                for link in links:
                    href = link["href"]
                    logger.info("checking_ddg_link", href=href)
                    if "masothue.com" in href:
                        parsed = urlparse(href)
                        qs = parse_qs(parsed.query)
                        uddg = qs.get("uddg", [None])[0]
                        if uddg and tax_code in uddg:
                            target_url = uddg
                            break
                            
                if target_url:
                    logger.info("fallback_url_found", url=target_url)
                    detail_html = await self.safe_get(target_url)
                    profile = await self.parse_business_detail(detail_html, target_url)
                    if profile.tax_code:
                        result.profile = profile
                        result.source_url = target_url
                        result.profile.source_url = target_url
            except Exception as e:
                logger.error("masothue_fallback_failed", error=str(e))
                
        if result.success:
            result.duration_ms = int((time.time() - start_time) * 1000)
            
        return result
