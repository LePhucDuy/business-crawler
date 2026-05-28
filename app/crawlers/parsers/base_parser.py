from abc import ABC, abstractmethod
from typing import Optional
from bs4 import BeautifulSoup
from app.domain.normalized import BusinessProfileNormalized

class BaseBusinessParser(ABC):
    provider_name: str

    @abstractmethod
    def parse_detail_page(self, html: str, source_url: str) -> BusinessProfileNormalized:
        pass

    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        element = soup.select_one(selector)
        if element:
            return self.normalize_whitespace(element.get_text(strip=True))
        return None

    def normalize_whitespace(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return " ".join(text.split())

    def calculate_confidence(self, profile: BusinessProfileNormalized) -> float:
        score = 0.0
        if profile.tax_code:
            score += 30
        if profile.business_name:
            score += 20
        if profile.address:
            score += 15
        if profile.legal_representative:
            score += 15
        if profile.status:
            score += 10
        if profile.source_url:
            score += 5
        if profile.crawled_at:
            score += 5
            
        return min(score, 100.0)
