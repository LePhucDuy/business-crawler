import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Navigate to a known tax code URL pattern
        await page.goto("https://thuvienphapluat.vn/ma-so-thue/0319490253.html", wait_until="networkidle")
        title = await page.title()
        url = page.url
        print(f"Title: {title}")
        print(f"URL: {url}")
        
        # also test search
        await page.goto("https://thuvienphapluat.vn/ma-so-thue?q=0319490253", wait_until="networkidle")
        print(f"Search URL: {page.url}")
        await browser.close()

asyncio.run(main())
