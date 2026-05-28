import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import time

async def main():
    async with async_playwright() as p:
        args = [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
        ]
        browser = await p.chromium.launch(headless=True, args=args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        # Apply stealth
        await Stealth().apply_stealth_async(page)
        
        try:
            print("Going to URL with stealth...")
            start = time.time()
            await page.goto("https://thuvienphapluat.vn/ma-so-thue/tra-cuu-ma-so-thue-doanh-nghiep?timtheo=ma-so-thue&tukhoa=0319490253", wait_until="networkidle", timeout=30000)
            print(f"Loaded in {time.time() - start}s")
            title = await page.title()
            print("Title:", title)
            html = await page.content()
            if "CÔNG TY CỔ PHẦN" in html:
                print("SUCCESS: Found company in HTML!")
            else:
                print("Failed to find company in HTML. Still blocked?")
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

asyncio.run(main())
