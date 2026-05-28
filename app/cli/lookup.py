import asyncio
import argparse
import json
from datetime import date, datetime
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.business_lookup_service import BusinessLookupService
from app.core.browser_manager import browser_manager
import app.crawlers.providers  # noqa: F401
from app.domain.schemas import BusinessLookupRequest

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

async def main():
    parser = argparse.ArgumentParser(description="Business Crawler CLI")
    parser.add_argument("--tax-code", type=str, help="Tax code to lookup")
    parser.add_argument("--name", type=str, help="Business name to lookup")
    parser.add_argument("--force-refresh", action="store_true", help="Force refresh data")
    
    args = parser.parse_args()
    
    if not args.tax_code and not args.name:
        print("Please provide --tax-code or --name")
        return
        
    async with AsyncSessionLocal() as session:
        service = BusinessLookupService(session)
        request = BusinessLookupRequest(
            tax_code=args.tax_code,
            name=args.name,
            force_refresh=args.force_refresh,
            providers=settings.ENABLED_PROVIDERS
        )
        
        try:
            await browser_manager.start()
            if args.tax_code:
                result = await service.lookup_by_tax_code(request)
                print(json.dumps(result.model_dump(), cls=DateTimeEncoder, indent=2, ensure_ascii=False))
            else:
                print("Name lookup CLI not fully implemented yet.")
        finally:
            await browser_manager.stop()
            await service.close()

if __name__ == "__main__":
    asyncio.run(main())
