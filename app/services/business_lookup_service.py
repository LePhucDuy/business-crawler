from typing import List, Optional
from datetime import datetime, timezone, timedelta
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.repositories.business_repository import BusinessRepository
from app.db.repositories.crawl_log_repository import CrawlLogRepository
from app.domain.schemas import BusinessLookupRequest, BusinessLookupResponse
from app.domain.enums import BusinessStatus
from app.services.business_merge_service import BusinessMergeService
from app.crawlers.manager import BusinessCrawlerManager
from app.services.normalization_service import NormalizationService
import structlog
from app.db.models import Business
from app.domain.normalized import BusinessProfileNormalized

logger = structlog.get_logger(__name__)

class BusinessLookupService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.business_repo = BusinessRepository(session)
        self.log_repo = CrawlLogRepository(session)
        self.merge_service = BusinessMergeService()
        self.http_client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS)
        self.crawler_manager = BusinessCrawlerManager(self.http_client)

    async def close(self):
        await self.http_client.aclose()

    def _is_cache_valid(self, business: Business) -> bool:
        if not business.last_checked_at:
            return False
            
        now = datetime.utcnow()
        last_checked = business.last_checked_at.replace(tzinfo=None) if business.last_checked_at.tzinfo else business.last_checked_at
        age_days = (now - last_checked).days
        
        if business.status == BusinessStatus.ACTIVE.value:
            return age_days < settings.CACHE_ACTIVE_DAYS
        elif business.status in (BusinessStatus.INACTIVE.value, BusinessStatus.SUSPENDED.value):
            return age_days < settings.CACHE_INACTIVE_DAYS
        else:
            return age_days < settings.CACHE_INCOMPLETE_DAYS

    async def lookup_by_tax_code(self, request: BusinessLookupRequest) -> BusinessLookupResponse:
        normalized_tax_code = NormalizationService.normalize_tax_code(request.tax_code)
        if not normalized_tax_code:
            return BusinessLookupResponse(success=False, needs_manual_review=False)

        # Check DB Cache
        cached_business = await self.business_repo.get_by_tax_code(normalized_tax_code)
        if cached_business and not request.force_refresh and self._is_cache_valid(cached_business):
            # Simplification: returning partial mapped data if cached
            profile_data = {k: v for k, v in cached_business.__dict__.items() if not k.startswith('_')}
            profile_data['source_name'] = cached_business.latest_source_name or "db_cache"
            return BusinessLookupResponse(
                success=True, 
                data=BusinessProfileNormalized(**profile_data),
                needs_manual_review=False
            )

        # Crawl
        job = await self.log_repo.create_crawl_job({
            "lookup_type": "tax_code",
            "lookup_value": normalized_tax_code,
            "status": "running",
            "provider_names": request.providers or settings.ENABLED_PROVIDERS,
            "started_at": datetime.utcnow()
        })
        await self.session.commit()

        provider_results = await self.crawler_manager.lookup_by_tax_code(normalized_tax_code, request.providers)
        
        # Merge
        merge_result = self.merge_service.merge_results(provider_results)
        
        # Save to DB
        if merge_result.final_profile.tax_code:
            business = await self.business_repo.upsert_business(merge_result.final_profile)
            business.last_checked_at = datetime.utcnow()
            
            for res in provider_results:
                await self.log_repo.add_business_source({
                    "business_id": business.id,
                    "tax_code": normalized_tax_code,
                    "source_name": res.provider_name,
                    "source_url": res.source_url,
                    "crawled_at": res.crawled_at,
                    "confidence_score": res.profile.confidence_score if res.profile else None,
                    "error_message": res.error_message,
                    "parsed_payload": res.profile.model_dump(mode='json') if res.profile else None
                })
        
        job.status = "success"
        job.finished_at = datetime.utcnow()
        await self.session.commit()

        return BusinessLookupResponse(
            success=True,
            data=merge_result.final_profile,
            provider_results=provider_results,
            needs_manual_review=merge_result.needs_manual_review,
            conflicts=merge_result.conflicts
        )
