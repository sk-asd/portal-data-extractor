import random
import time


class ProxyPool:
    def __init__(self, path="proxies.txt", cooldown=300):
        self.path = path
        self.cooldown = cooldown
        self.items = []
        self.bad = {}
        self.stats = {}

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.items = [x.strip() for x in f if x.strip()]
        except FileNotFoundError:
            self.items = []

        for p in self.items:
            self.stats.setdefault(p, {"ok": 0, "fail": 0})

        return len(self.items)

    def pick(self):
        now = time.time()
        ready = [p for p in self.items if self.bad.get(p, 0) < now]
        if not ready:
            return None

        ready.sort(key=lambda p: self.stats[p]["fail"] - self.stats[p]["ok"])
        return random.choice(ready[: min(5, len(ready))])

    def ok(self, proxy):
        if not proxy:
            return
        self.stats.setdefault(proxy, {"ok": 0, "fail": 0})
        self.stats[proxy]["ok"] += 1

    def fail(self, proxy):
        if not proxy:
            return
        self.stats.setdefault(proxy, {"ok": 0, "fail": 0})
        self.stats[proxy]["fail"] += 1

        s = self.stats[proxy]
        if s["fail"] >= 3 and s["fail"] > s["ok"]:
            self.bad[proxy] = time.time() + self.cooldown


def as_playwright_proxy(proxy):
    if not proxy:
        return None
    if "://" not in proxy:
        proxy = "http://" + proxy
    return {"server": proxy}
