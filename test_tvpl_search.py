import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Go to the search page
        await page.goto("https://thuvienphapluat.vn/ma-so-thue?q=0319490253", wait_until="networkidle")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the search results
        links = soup.select(".company-item a.company-name")
        for link in links:
            print(f"Found link: {link.get('href')}")
            
        await browser.close()

asyncio.run(main())
