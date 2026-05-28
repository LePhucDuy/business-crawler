class CrawlerBaseException(Exception):
    """Base exception for all crawler related errors"""
    pass

class ProviderTimeoutError(CrawlerBaseException):
    pass

class ProviderCaptchaDetected(CrawlerBaseException):
    def __init__(self, provider_name: str, message: str = "Captcha detected"):
        self.provider_name = provider_name
        self.message = message
        super().__init__(self.message)

class ProviderNotSupported(CrawlerBaseException):
    pass

class ProviderRateLimited(CrawlerBaseException):
    pass

class ProviderParseError(CrawlerBaseException):
    pass

class ProviderManualReviewRequired(CrawlerBaseException):
    def __init__(self, provider_name: str, message: str = "Manual review required"):
        self.provider_name = provider_name
        self.message = message
        super().__init__(self.message)

class InvalidTaxCodeError(CrawlerBaseException):
    pass

class CrawlPolicyViolation(CrawlerBaseException):
    """Raised when a crawling policy is violated (e.g. domain not allowed)"""
    pass
