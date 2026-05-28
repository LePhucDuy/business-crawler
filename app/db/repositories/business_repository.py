from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Business, BusinessSource
from app.domain.normalized import BusinessProfileNormalized
from typing import Optional

class BusinessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tax_code(self, tax_code: str) -> Optional[Business]:
        stmt = select(Business).where(Business.tax_code == tax_code)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_name(self, name: str, limit: int = 10) -> list[Business]:
        stmt = select(Business).where(Business.normalized_business_name.ilike(f"%{name}%")).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_business(self, profile: BusinessProfileNormalized) -> Business:
        existing = None
        if profile.tax_code:
            existing = await self.get_by_tax_code(profile.tax_code)
            
        if existing:
            for key, value in profile.model_dump(exclude_unset=True).items():
                if hasattr(existing, key) and key not in ['raw_payload', 'source_name', 'source_url', 'crawled_at']:
                    setattr(existing, key, value)
            existing.latest_source_name = profile.source_name
            existing.latest_source_url = profile.source_url
            existing.confidence_score = profile.confidence_score
            return existing
        
        # Create new
        data = profile.model_dump(exclude={'raw_payload'})
        # exclude fields not in Business model
        data = {k: v for k, v in data.items() if hasattr(Business, k)}
        data['latest_source_name'] = profile.source_name
        data['latest_source_url'] = profile.source_url
        new_business = Business(**data)
        self.session.add(new_business)
        return new_business
