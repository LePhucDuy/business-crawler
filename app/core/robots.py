import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict
import httpx
import structlog

logger = structlog.get_logger(__name__)

class RobotsChecker:
    def __init__(self):
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    async def is_allowed(self, url: str, user_agent: str) -> bool:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base_url}/robots.txt"

        if base_url not in self._parsers:
            rp = urllib.robotparser.RobotFileParser()
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(robots_url)
                    if response.status_code == 200:
                        rp.parse(response.text.splitlines())
                    else:
                        rp.allow_all = True
            except Exception as e:
                logger.warning("robots_fetch_failed", url=robots_url, error=str(e))
                rp.allow_all = True
            self._parsers[base_url] = rp

        parser = self._parsers[base_url]
        if getattr(parser, "allow_all", False):
            return True
            
        return parser.can_fetch(user_agent, url)

robots_checker = RobotsChecker()
