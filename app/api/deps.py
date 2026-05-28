from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.business_lookup_service import BusinessLookupService

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

def get_lookup_service(session: AsyncSession = Depends(get_db)) -> BusinessLookupService:
    return BusinessLookupService(session)
