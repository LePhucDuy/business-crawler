from urllib.parse import urlparse
from app.core.config import settings
from app.core.exceptions import CrawlPolicyViolation
import structlog

logger = structlog.get_logger(__name__)

class CrawlPolicy:
    @classmethod
    def check_url_allowed(cls, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
            
        is_allowed = any(domain == allowed or domain.endswith("." + allowed) for allowed in settings.ALLOWED_DOMAINS)
        
        if not is_allowed:
            logger.warning("crawl_policy_violation", reason="domain_not_allowed", url=url, domain=domain)
            raise CrawlPolicyViolation(f"Domain {domain} is not in ALLOWED_DOMAINS")
        
        return True

    @classmethod
    def enforce_no_captcha_bypass(cls, provider_name: str, requires_captcha: bool):
        if requires_captcha and not settings.ALLOW_MANUAL_CAPTCHA:
            logger.info("crawl_policy_enforcement", reason="captcha_required", provider=provider_name)
            # This is handled upstream by returning a MANUAL_REQUIRED status
            return False
        return True
