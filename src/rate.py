import asyncio
import random
import time


class Pace:
    def __init__(self, per_sec=2):
        self.delay = 1 / max(per_sec, 0.1)
        self.last = 0.0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = time.monotonic()
            left = self.delay - (now - self.last)
            if left > 0:
                await asyncio.sleep(left + random.uniform(0.02, 0.12))
            self.last = time.monotonic()
