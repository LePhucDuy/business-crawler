from app.crawlers.registry import crawler_registry
from app.crawlers.providers.gdt.crawler import GDTCrawler
from app.crawlers.providers.masothue.crawler import MasothueCrawler
from app.crawlers.providers.vietqr.crawler import VietQRCrawler
from app.crawlers.providers.thuvienphapluat.crawler import ThuvienphapluatCrawler

# Auto register providers
crawler_registry.register("gdt", GDTCrawler)
crawler_registry.register("masothue", MasothueCrawler)
crawler_registry.register("vietqr", VietQRCrawler)
crawler_registry.register("thuvienphapluat", ThuvienphapluatCrawler)
