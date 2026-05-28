from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Business Crawler API"
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/business_crawler"
    
    HTTP_TIMEOUT_SECONDS: int = 15
    HTTP_MAX_RETRIES: int = 3
    DEFAULT_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    ENABLED_PROVIDERS: List[str] = ["masothue", "gdt"]
    MAX_CONCURRENT_PROVIDERS: int = 3
    
    # Strategy: "parallel" (run all enabled concurrently) or "fallback" (run sequentially, stop on first success)
    CRAWL_STRATEGY: str = "fallback"
    
    CACHE_ACTIVE_DAYS: int = 14
    CACHE_INACTIVE_DAYS: int = 3
    CACHE_INCOMPLETE_DAYS: int = 1
    
    ALLOW_MANUAL_CAPTCHA: bool = False

    # Rate Limiting (chống spam API)
    RATE_LIMIT_REQUESTS: int = 60   # Số request tối đa
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # Trong khoảng thời gian (giây)
    
    STORE_RAW_HTML: bool = False
    RAW_HTML_STORAGE_DIR: str = "./storage/raw_snapshots"
    
    ALLOWED_DOMAINS: List[str] = ["masothue.com", "gdt.gov.vn", "tracuunnt.gdt.gov.vn", "api.vietqr.io"]
    
    @field_validator("ENABLED_PROVIDERS", "ALLOWED_DOMAINS", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            # Thử parse JSON array trước (ví dụ: '["masothue","gdt"]')
            if v.startswith("["):
                import json
                try:
                    result = json.loads(v)
                    if isinstance(result, list):
                        return [str(i).strip() for i in result]
                except json.JSONDecodeError:
                    pass
            # Fallback: tách theo dấu phẩy
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
        
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
