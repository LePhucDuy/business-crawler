import asyncio
from playwright.async_api import async_playwright

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Go to the search page
            await page.goto("https://thuvienphapluat.vn/ma-so-thue?q=0319490253", wait_until="load", timeout=15000)
            
            # Print page title
            print("Title:", await page.title())
            
            # Save HTML
            html = await page.content()
            with open("tvpl_test.html", "w") as f:
                f.write(html)
                
            await browser.close()
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
