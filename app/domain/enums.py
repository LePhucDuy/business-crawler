from enum import Enum

class BusinessStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    UNKNOWN = "UNKNOWN"

class LookupType(str, Enum):
    TAX_CODE = "tax_code"
    NAME = "name"

class ProviderCapability(str, Enum):
    TAX_CODE_LOOKUP = "tax_code_lookup"
    NAME_LOOKUP = "name_lookup"
    DETAIL_LOOKUP = "detail_lookup"
    MANUAL_REVIEW = "manual_review"

class ProviderResultStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    NOT_SUPPORTED = "not_supported"
    CAPTCHA_DETECTED = "captcha_detected"
    MANUAL_REQUIRED = "manual_required"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"

class CrawlJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
