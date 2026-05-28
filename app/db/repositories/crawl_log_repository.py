from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import BusinessSource, CrawlJob
from typing import Dict, Any, Optional

class CrawlLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_business_source(self, source_data: Dict[str, Any]) -> BusinessSource:
        source = BusinessSource(**source_data)
        self.session.add(source)
        return source

    async def create_crawl_job(self, job_data: Dict[str, Any]) -> CrawlJob:
        job = CrawlJob(**job_data)
        self.session.add(job)
        return job
