from app.crawlers.browser import BrowserBusinessCrawler
from app.domain.enums import ProviderCapability
from app.domain.normalized import BusinessProfileNormalized
from app.crawlers.providers.thuvienphapluat.parser import ThuvienphapluatParser
from bs4 import BeautifulSoup
from app.domain.schemas import ProviderResult
from app.core.exceptions import ProviderTimeoutError, ProviderCaptchaDetected
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
        return f"{self.base_url}/ma-so-thue/tra-cuu-ma-so-thue-doanh-nghiep?timtheo=ma-so-thue&tukhoa={tax_code}"
        
    async def build_name_search_url(self, name: str) -> str:
        raise NotImplementedError("Thuvienphapluat provider only supports tax_code lookup via this interface")
        
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        return self.parser.parse_detail_page(html, source_url)

    async def lookup_by_tax_code(self, tax_code: str) -> ProviderResult:
        start_time = time.time()
        try:
            await self.validate_before_request()
            search_url = await self.build_tax_code_url(tax_code)
            
            # Manually manage context to share Cloudflare clearance across both requests
            from app.core.browser_manager import browser_manager
            from app.core.config import settings
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            
            browser = await browser_manager.get_browser()
            context = await browser.new_context(
                user_agent=settings.DEFAULT_USER_AGENT,
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()
            
            try:
                from playwright_stealth import Stealth
                await Stealth().apply_stealth_async(page)
            except Exception as e:
                logger.warning("playwright_stealth_failed", error=str(e))
                
            try:
                # 1. Fetch Search Page
                logger.info("thuvienphapluat_search_start", url=search_url)
                try:
                    await page.goto(search_url, timeout=settings.HTTP_TIMEOUT_SECONDS * 1000, wait_until="domcontentloaded")
                except PlaywrightTimeoutError:
                    pass
                    
                for _ in range(15):
                    try:
                        html = await page.content()
                        if "cf-browser-verification" not in html and "Just a moment..." not in html:
                            break
                    except Exception:
                        pass
                    await page.wait_for_timeout(1000)
                    
                await page.wait_for_timeout(2000)
                html = await page.content()
                
                if self.detect_captcha(html) or "cf-browser-verification" in html or "Just a moment..." in html:
                    raise ProviderCaptchaDetected(self.provider_name)
                
                # Extract first result
                soup = BeautifulSoup(html, "html.parser")
                target_url = None
                
                links = soup.select("a")
                for link in links:
                    href = link.get("href", "")
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
                    
                # 2. Fetch Detail Page (Reusing the same cleared page!)
                logger.info("thuvienphapluat_fetching_detail", url=target_url)
                try:
                    await page.goto(target_url, timeout=settings.HTTP_TIMEOUT_SECONDS * 1000, wait_until="domcontentloaded")
                except PlaywrightTimeoutError:
                    pass
                    
                for _ in range(15):
                    try:
                        detail_html = await page.content()
                        if "cf-browser-verification" not in detail_html and "Just a moment..." not in detail_html:
                            break
                    except Exception:
                        pass
                    await page.wait_for_timeout(1000)
                    
                await page.wait_for_timeout(2000)
                detail_html = await page.content()
                
                if self.detect_captcha(detail_html) or "cf-browser-verification" in detail_html or "Just a moment..." in detail_html:
                    raise ProviderCaptchaDetected(self.provider_name)
                    
                profile = await self.parse_business_detail(detail_html, target_url)
                
                duration_ms = int((time.time() - start_time) * 1000)
                return ProviderResult.success_result(
                    provider_name=self.provider_name,
                    profile=profile,
                    source_url=target_url,
                    duration_ms=duration_ms
                )
                
            finally:
                await context.close()

        except (ProviderTimeoutError, ProviderCaptchaDetected) as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info("thuvienphapluat_blocked_or_timeout", error=str(e))
            from app.domain.enums import ProviderResultStatus
            return ProviderResult(
                provider_name=self.provider_name,
                success=False,
                status=ProviderResultStatus.FAILED,
                error_message="Not found or blocked by Cloudflare (Timeout/Captcha)",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error("thuvienphapluat_error", error=str(e), exc_info=True)
            from app.domain.enums import ProviderResultStatus
            return ProviderResult(
                provider_name=self.provider_name,
                success=False,
                status=ProviderResultStatus.FAILED,
                error_message=str(e),
                duration_ms=duration_ms
            )
