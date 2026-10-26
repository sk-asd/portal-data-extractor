import asyncio
import random
import re


def clean(txt):
    return re.sub(r"\s+", " ", txt or "").strip()


async def retry(label, max_try, fn):
    last_err = None

    for i in range(1, max_try + 1):
        try:
            return await fn()
        except Exception as err:
            last_err = err
            delay = 0.4 * i + random.uniform(0.1, 0.7)
            print(f"[retry] {label} failed {i}/{max_try}, waiting {delay:.1f}s")
            await asyncio.sleep(delay)

    raise last_err
