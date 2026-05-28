from app.crawlers.registry import crawler_registry
from app.crawlers.providers.gdt.crawler import GDTCrawler
from app.crawlers.providers.masothue.crawler import MasothueCrawler

# Auto register providers
crawler_registry.register("gdt", GDTCrawler)
crawler_registry.register("masothue", MasothueCrawler)
