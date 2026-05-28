import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Playwright, Browser
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

class PlaywrightBrowserManager:
    _instance = None

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start(self):
        if self.browser:
            return
            
        logger.info("starting_playwright_browser")
        self.playwright = await async_playwright().start()
        
        launch_kwargs = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"]
        }
        
        if settings.BRAVE_EXECUTABLE_PATH:
            logger.info("using_custom_executable", executable_path=settings.BRAVE_EXECUTABLE_PATH)
            launch_kwargs["executable_path"] = settings.BRAVE_EXECUTABLE_PATH
            
        try:
            self.browser = await self.playwright.chromium.launch(**launch_kwargs)
            logger.info("playwright_browser_started")
        except Exception as e:
            logger.error("failed_to_start_browser", error=str(e), exc_info=True)
            raise

    async def stop(self):
        logger.info("stopping_playwright_browser")
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.info("playwright_browser_stopped")

    async def get_browser(self) -> Browser:
        if not self.browser:
            await self.start()
        return self.browser

browser_manager = PlaywrightBrowserManager.get_instance()
