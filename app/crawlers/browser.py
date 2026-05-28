import time
import structlog
from typing import Optional
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.core.config import settings
from app.core.exceptions import ProviderCaptchaDetected, ProviderTimeoutError
from app.crawlers.base import BaseBusinessCrawler
from app.core.browser_manager import browser_manager

logger = structlog.get_logger(__name__)

class BrowserBusinessCrawler(BaseBusinessCrawler):
    """
    Crawler that uses Playwright (Brave/Chromium) to render JS and bypass basic Cloudflare checks.
    """
    
    async def safe_get(self, url: str) -> str:
        """Override safe_get to use Playwright instead of httpx."""
        start_time = time.time()
        logger.info("browser_request_start", provider=self.provider_name, url=url)
        
        browser = await browser_manager.get_browser()
        # Create a new context per request for isolation (clears cookies/cache)
        context = await browser.new_context(
            user_agent=settings.DEFAULT_USER_AGENT,
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        try:
            # Navigate to the URL and wait until network is idle (to let JS Cloudflare challenges finish)
            response = await page.goto(
                url, 
                timeout=settings.HTTP_TIMEOUT_SECONDS * 1000,
                wait_until="networkidle"
            )
            
            if not response:
                raise ProviderTimeoutError(self.provider_name, "Empty response from browser")
                
            # Allow an extra 3 seconds just in case there's a meta refresh or delayed CF redirect
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            
            # Check for Cloudflare block pages that didn't pass
            if self.detect_captcha(html) or "cf-browser-verification" in html or response.status in (401, 403):
                raise ProviderCaptchaDetected(self.provider_name)
                
            return html
            
        except PlaywrightTimeoutError:
            raise ProviderTimeoutError(self.provider_name)
        except ProviderCaptchaDetected:
            raise
        except Exception as e:
            logger.error("browser_request_error", error=str(e), provider=self.provider_name)
            raise
        finally:
            await context.close()
            duration = int((time.time() - start_time) * 1000)
            logger.info("browser_request_end", provider=self.provider_name, url=url, duration_ms=duration)
