from app.crawlers.browser import BrowserBusinessCrawler
from app.domain.enums import ProviderCapability
from app.domain.normalized import BusinessProfileNormalized
from app.crawlers.providers.thuvienphapluat.parser import ThuvienphapluatParser
from bs4 import BeautifulSoup
from app.domain.schemas import ProviderResult
import time
import structlog
from urllib.parse import urljoin

logger = structlog.get_logger(__name__)

class ThuvienphapluatCrawler(BrowserBusinessCrawler):
    provider_name = "thuvienphapluat"
    base_url = "https://thuvienphapluat.vn"
    capabilities = [ProviderCapability.TAX_CODE_LOOKUP]
    requires_captcha = False
    rate_limit_per_minute = 15
    
    def __init__(self, http_client):
        super().__init__(http_client)
        self.parser = ThuvienphapluatParser()
        
    async def build_tax_code_url(self, tax_code: str) -> str:
        return f"{self.base_url}/ma-so-thue?q={tax_code}"
        
    async def build_name_search_url(self, name: str) -> str:
        raise NotImplementedError("Thuvienphapluat provider only supports tax_code lookup via this interface")
        
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        return self.parser.parse_detail_page(html, source_url)

    async def lookup_by_tax_code(self, tax_code: str) -> ProviderResult:
        start_time = time.time()
        try:
            await self.validate_before_request()
            search_url = await self.build_tax_code_url(tax_code)
            
            # Fetch search page
            html = await self.safe_get(search_url)
            
            # Extract first result
            soup = BeautifulSoup(html, "html.parser")
            
            # Usually TVPL search results have specific classes, try a few common ones
            target_url = None
            
            # TVPL might redirect directly if there's only 1 match
            if "-mst-" in search_url or "/ma-so-thue/" in html:
                # Need to verify if it redirected
                pass

            # Find links in search results
            links = soup.select("a")
            for link in links:
                href = link.get("href", "")
                # Expected format: /ma-so-thue/cong-ty-co-phan-dau-tu-phat-trien-dhf-holdings-mst-0319490253.html
                if "-mst-" in href and tax_code in href and href.endswith(".html"):
                    target_url = href
                    if not target_url.startswith("http"):
                        target_url = urljoin(self.base_url, target_url)
                    break
                    
            if not target_url:
                logger.info("thuvienphapluat_no_search_results", tax_code=tax_code)
                from app.domain.enums import ProviderResultStatus
                return ProviderResult(
                    provider_name=self.provider_name,
                    success=False,
                    status=ProviderResultStatus.FAILED,
                    error_message="Not found or blocked by Cloudflare",
                    duration_ms=int((time.time() - start_time) * 1000)
                )
                
            # Now fetch the detail page
            logger.info("thuvienphapluat_fetching_detail", url=target_url)
            detail_html = await self.safe_get(target_url)
            profile = await self.parse_business_detail(detail_html, target_url)
            
            duration_ms = int((time.time() - start_time) * 1000)
            return ProviderResult.success_result(
                provider_name=self.provider_name,
                profile=profile,
                source_url=target_url,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error("thuvienphapluat_error", error=str(e), exc_info=True)
            return ProviderResult(
                provider_name=self.provider_name,
                success=False,
                status="failed",
                error_message=str(e),
                duration_ms=duration_ms
            )
