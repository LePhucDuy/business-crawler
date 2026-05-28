import asyncio
from typing import List, Optional
import httpx
from app.core.config import settings
from app.crawlers.registry import crawler_registry
from app.domain.schemas import ProviderResult
import structlog

logger = structlog.get_logger(__name__)

class BusinessCrawlerManager:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def lookup_by_tax_code(self, tax_code: str, provider_names: Optional[List[str]] = None) -> List[ProviderResult]:
        target_providers = provider_names if provider_names else settings.ENABLED_PROVIDERS
        crawlers = crawler_registry.get_all_supporting_tax_code(target_providers)
        
        if not crawlers:
            return []

        final_results = []
        
        if settings.CRAWL_STRATEGY == "fallback":
            for crawler_class in crawlers:
                crawler = crawler_class(self.http_client)
                try:
                    res = await crawler.lookup_by_tax_code(tax_code)
                    final_results.append(res)
                    if res.success and res.profile and res.profile.tax_code:
                        logger.info("fallback_strategy_success", provider=crawler.provider_name)
                        break
                except Exception as e:
                    logger.error("crawler_manager_exception", provider=crawler.provider_name, error=str(e), exc_info=True)
                    final_results.append(ProviderResult(
                        provider_name=crawler.provider_name,
                        success=False,
                        status="failed",
                        error_message=str(e)
                    ))
        else:
            tasks = []
            for crawler_class in crawlers:
                crawler = crawler_class(self.http_client)
                tasks.append(crawler.lookup_by_tax_code(tax_code))
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, res in enumerate(results):
                provider_name = crawlers[i].provider_name
                if isinstance(res, Exception):
                    logger.error("crawler_manager_exception", provider=provider_name, error=str(res), exc_info=True)
                    final_results.append(ProviderResult(
                        provider_name=provider_name,
                        success=False,
                        status="failed",
                        error_message=str(res)
                    ))
                else:
                    final_results.append(res)
                    
        return final_results

    async def lookup_by_name(self, name: str, provider_names: Optional[List[str]] = None) -> List[List[ProviderResult]]:
        target_providers = provider_names if provider_names else settings.ENABLED_PROVIDERS
        crawlers = crawler_registry.get_all_supporting_name(target_providers)
        
        if not crawlers:
            return []

        final_results = []
        
        if settings.CRAWL_STRATEGY == "fallback":
            for crawler_class in crawlers:
                crawler = crawler_class(self.http_client)
                try:
                    res = await crawler.lookup_by_name(name)
                    final_results.append(res)
                    # If this provider returned any results, stop
                    if res and any(r.success and r.profile for r in res):
                        logger.info("fallback_strategy_success", provider=crawler.provider_name)
                        break
                except Exception as e:
                    logger.error("crawler_manager_exception", provider=crawler.provider_name, error=str(e), exc_info=True)
                    final_results.append([ProviderResult(
                        provider_name=crawler.provider_name,
                        success=False,
                        status="failed",
                        error_message=str(e)
                    )])
        else:
            tasks = []
            for crawler_class in crawlers:
                crawler = crawler_class(self.http_client)
                tasks.append(crawler.lookup_by_name(name))
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, res in enumerate(results):
                provider_name = crawlers[i].provider_name
                if isinstance(res, Exception):
                    logger.error("crawler_manager_exception", provider=provider_name, error=str(res), exc_info=True)
                    final_results.append([ProviderResult(
                        provider_name=provider_name,
                        success=False,
                        status="failed",
                        error_message=str(res)
                    )])
                else:
                    final_results.append(res)
                    
        return final_results
