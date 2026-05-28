import asyncio
import time
from typing import Dict

class RateLimiter:
    """
    Simple in-memory rate limiter per domain.
    For production, this should be backed by Redis.
    """
    def __init__(self):
        self._domain_locks: Dict[str, asyncio.Lock] = {}
        self._last_request_time: Dict[str, float] = {}

    def _get_lock(self, domain: str) -> asyncio.Lock:
        if domain not in self._domain_locks:
            self._domain_locks[domain] = asyncio.Lock()
        return self._domain_locks[domain]

    async def acquire(self, domain: str, rpm: int):
        if rpm <= 0:
            return
            
        min_interval = 60.0 / rpm
        lock = self._get_lock(domain)
        
        async with lock:
            now = time.time()
            last_time = self._last_request_time.get(domain, 0.0)
            elapsed = now - last_time
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
                
            self._last_request_time[domain] = time.time()

rate_limiter = RateLimiter()
