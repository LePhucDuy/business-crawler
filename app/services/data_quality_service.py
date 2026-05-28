from app.domain.normalized import BusinessProfileNormalized

class DataQualityService:
    @staticmethod
    def calculate_confidence(profile: BusinessProfileNormalized) -> float:
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
