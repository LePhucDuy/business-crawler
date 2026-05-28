from abc import ABC, abstractmethod
from typing import List, Optional, Any
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.exceptions import (
    ProviderCaptchaDetected,
    ProviderManualReviewRequired,
    ProviderRateLimited,
    ProviderTimeoutError,
)
from app.core.rate_limiter import rate_limiter
from app.core.crawl_policy import CrawlPolicy
from app.core.robots import robots_checker
from app.domain.enums import ProviderCapability
from app.domain.schemas import ProviderResult
from app.domain.normalized import BusinessProfileNormalized
import structlog

logger = structlog.get_logger(__name__)

class BaseBusinessCrawler(ABC):
    provider_name: str
    base_url: str
    capabilities: List[ProviderCapability] = []
    requires_captcha: bool = False
    rate_limit_per_minute: int = 10
    supports_bulk: bool = False

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def validate_before_request(self):
        if self.requires_captcha and not settings.ALLOW_MANUAL_CAPTCHA:
            raise ProviderManualReviewRequired(self.provider_name)
            
        CrawlPolicy.check_url_allowed(self.base_url)
        
        is_allowed = await robots_checker.is_allowed(self.base_url, settings.DEFAULT_USER_AGENT)
        if not is_allowed:
            logger.warning("robots_txt_disallowed", provider=self.provider_name, url=self.base_url)
            raise ProviderManualReviewRequired(self.provider_name, message="Blocked by robots.txt")
            
        await rate_limiter.acquire(self.provider_name, self.rate_limit_per_minute)

    @retry(
        stop=stop_after_attempt(settings.HTTP_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def safe_get(self, url: str) -> str:
        start_time = time.time()
        try:
            logger.info("http_request_start", provider=self.provider_name, url=url)
            # Add user agent header to respect best practices
            headers = {"User-Agent": settings.DEFAULT_USER_AGENT}
            response = await self.http_client.get(url, timeout=settings.HTTP_TIMEOUT_SECONDS, headers=headers, follow_redirects=True)
            response.raise_for_status()
            
            if self.detect_captcha(response.text):
                raise ProviderCaptchaDetected(self.provider_name)
                
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                raise ProviderCaptchaDetected(self.provider_name, message=f"HTTP {e.response.status_code}")
            if e.response.status_code == 429:
                raise ProviderRateLimited(self.provider_name)
            raise
        finally:
            duration = int((time.time() - start_time) * 1000)
            logger.info("http_request_end", provider=self.provider_name, url=url, duration_ms=duration)

    async def lookup_by_tax_code(self, tax_code: str) -> ProviderResult:
        if ProviderCapability.TAX_CODE_LOOKUP not in self.capabilities:
            return ProviderResult.not_supported(self.provider_name)

        start_time = time.time()
        try:
            await self.validate_before_request()
            url = await self.build_tax_code_url(tax_code)
            html = await self.safe_get(url)
            profile = await self.parse_business_detail(html, url)
            
            duration_ms = int((time.time() - start_time) * 1000)
            return ProviderResult.success_result(
                provider_name=self.provider_name,
                profile=profile,
                source_url=url,
                duration_ms=duration_ms
            )
        except ProviderManualReviewRequired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return ProviderResult(
                provider_name=self.provider_name,
                success=False,
                status="manual_required",
                manual_review_reason=e.message,
                duration_ms=duration_ms
            )
        except ProviderCaptchaDetected as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return ProviderResult.captcha_detected(self.provider_name)
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error("provider_error", provider=self.provider_name, error=str(e), exc_info=True)
            return ProviderResult(
                provider_name=self.provider_name,
                success=False,
                status="failed",
                error_message=str(e),
                duration_ms=duration_ms
            )

    async def lookup_by_name(self, name: str) -> List[ProviderResult]:
        if ProviderCapability.NAME_LOOKUP not in self.capabilities:
            return [ProviderResult.not_supported(self.provider_name)]
            
        start_time = time.time()
        try:
            await self.validate_before_request()
            url = await self.build_name_search_url(name)
            html = await self.safe_get(url)
            results = await self.parse_search_results(html, url)
            
            duration_ms = int((time.time() - start_time) * 1000)
            for res in results:
                res.duration_ms = duration_ms
            return results
        except Exception as e:
            logger.error("provider_error", provider=self.provider_name, error=str(e), exc_info=True)
            return [ProviderResult(
                provider_name=self.provider_name,
                success=False,
                status="failed",
                error_message=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )]

    @abstractmethod
    async def build_tax_code_url(self, tax_code: str) -> str:
        pass

    @abstractmethod
    async def build_name_search_url(self, name: str) -> str:
        pass

    @abstractmethod
    async def parse_business_detail(self, html: str, source_url: str) -> BusinessProfileNormalized:
        pass

    async def parse_search_results(self, html: str, source_url: str) -> List[ProviderResult]:
        return []

    def detect_captcha(self, html: str) -> bool:
        keywords = [
            "vui lòng xác nhận bạn là con người",
            "cf-browser-verification",
            "just a moment..."
        ]
        lower_html = html.lower()
        return any(keyword in lower_html for keyword in keywords)
