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
            from playwright_stealth import Stealth
            await Stealth().apply_stealth_async(page)
        except Exception as e:
            logger.warning("playwright_stealth_failed", error=str(e))
        
        try:
            logger.info("browser_using_ua", ua=settings.DEFAULT_USER_AGENT)
            
            # Navigate to the URL and wait for domcontentloaded instead of networkidle
            # networkidle might timeout if background trackers keep connections open
            try:
                response = await page.goto(
                    url, 
                    timeout=settings.HTTP_TIMEOUT_SECONDS * 1000,
                    wait_until="domcontentloaded"
                )
            except PlaywrightTimeoutError:
                logger.warning("browser_goto_timeout", provider=self.provider_name)
                
            # Wait for Cloudflare to solve itself (usually takes 5-15s)
            for _ in range(15):
                html = await page.content()
                if "cf-browser-verification" not in html and "Just a moment..." not in html and "DDoS protection" not in html:
                    # Not on a Cloudflare challenge page anymore!
                    break
                await page.wait_for_timeout(1000)
                
            # Allow an extra 2 seconds for the actual app to render after CF redirects
            await page.wait_for_timeout(2000)
            
            html = await page.content()
            
            # Check for Cloudflare block pages that didn't pass
            if self.detect_captcha(html) or "cf-browser-verification" in html or "Just a moment..." in html:
                raise ProviderCaptchaDetected(self.provider_name)
                
            return html
            
        except ProviderCaptchaDetected:
            raise
        except Exception as e:
            logger.error("browser_request_error", error=str(e), provider=self.provider_name)
            raise
        finally:
            await context.close()
            duration = int((time.time() - start_time) * 1000)
            logger.info("browser_request_end", provider=self.provider_name, url=url, duration_ms=duration)
