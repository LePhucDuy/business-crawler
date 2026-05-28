from typing import Dict, Type, List, Optional
from app.crawlers.base import BaseBusinessCrawler
from app.domain.enums import ProviderCapability
import structlog

logger = structlog.get_logger(__name__)

class CrawlerRegistry:
    def __init__(self):
        self._crawlers: Dict[str, Type[BaseBusinessCrawler]] = {}

    def register(self, provider_name: str, crawler_class: Type[BaseBusinessCrawler]):
        if provider_name in self._crawlers:
            logger.warning("crawler_override", provider_name=provider_name)
        self._crawlers[provider_name] = crawler_class
        logger.info("crawler_registered", provider_name=provider_name)

    def get(self, provider_name: str) -> Optional[Type[BaseBusinessCrawler]]:
        return self._crawlers.get(provider_name)

    def list_enabled(self, enabled_names: List[str]) -> List[Type[BaseBusinessCrawler]]:
        return [
            self._crawlers[name]
            for name in enabled_names
            if name in self._crawlers
        ]

    def get_all_supporting_tax_code(self, enabled_names: List[str]) -> List[Type[BaseBusinessCrawler]]:
        enabled = self.list_enabled(enabled_names)
        return [c for c in enabled if ProviderCapability.TAX_CODE_LOOKUP in c.capabilities]

    def get_all_supporting_name(self, enabled_names: List[str]) -> List[Type[BaseBusinessCrawler]]:
        enabled = self.list_enabled(enabled_names)
        return [c for c in enabled if ProviderCapability.NAME_LOOKUP in c.capabilities]

crawler_registry = CrawlerRegistry()
