import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Going to URL...")
            start = time.time()
            await page.goto("https://thuvienphapluat.vn/ma-so-thue/tra-cuu-ma-so-thue-doanh-nghiep?timtheo=ma-so-thue&tukhoa=0319490253", wait_until="networkidle", timeout=45000)
            print(f"Loaded in {time.time() - start}s")
            title = await page.title()
            print("Title:", title)
            html = await page.content()
            if "CÔNG TY CỔ PHẦN" in html:
                print("SUCCESS: Found company in HTML!")
            else:
                print("Failed to find company in HTML.")
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

asyncio.run(main())
