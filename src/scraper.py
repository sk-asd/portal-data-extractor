import asyncio
import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from config import config
from exporter import save
from helpers import clean, retry
from proxy_pool import ProxyPool, as_playwright_proxy
from rate import Pace


STATE_PATH = os.path.join("storage", "portal_state.json")


async def login_if_needed(page):
    await page.goto(config["base_url"] + "/clients")
    if "/login" not in page.url:
        return

    await page.fill('input[name="user"]', config["user"])
    await page.fill('input[name="pass"]', config["pass"])
    await page.click("button")
    await page.wait_for_url("**/clients", timeout=8000)


async def collect_links(page, pace):
    links = []
    next_url = config["base_url"] + "/clients?page=1"

    while next_url:
        async def go():
            await pace.wait()
            await page.goto(next_url, wait_until="domcontentloaded")
            await page.wait_for_selector("table.clients", timeout=5000)

        await retry(f"list {next_url}", config["max_retry"], go)

        soup = BeautifulSoup(await page.content(), "lxml")
        for tr in soup.select("table.clients tbody tr"):
            cols = [clean(td.get_text()) for td in tr.select("td")]
            a = tr.select_one("a[href]")
            if len(cols) >= 2 and a:
                links.append({
                    "id": cols[0],
                    "name": cols[1],
                    "href": urljoin(config["base_url"], a["href"]),
                })

        nxt = soup.select_one("a.next[href]")
        next_url = urljoin(config["base_url"], nxt["href"]) if nxt else ""

    return links


async def scrape_one(ctx, link, sem, pace):
    async with sem:
        page = await ctx.new_page()

        async def run():
            await pace.wait()
            await page.goto(link["href"], wait_until="domcontentloaded")
            await page.wait_for_selector("[data-client]", timeout=5000)
            soup = BeautifulSoup(await page.content(), "lxml")

            root = soup.select_one("[data-client]")
            pick = lambda sel: clean(root.select_one(sel).get_text()) if root and root.select_one(sel) else ""
            payments = []
            for tr in soup.select("table.payments tbody tr"):
                cols = [clean(td.get_text()) for td in tr.select("td")]
                if len(cols) >= 3:
                    payments.append({"date": cols[0], "desc": cols[1], "amount": cols[2]})

            return {
                "id": root.get("data-client", "") if root else link["id"],
                "name": pick("[data-name]") or link["name"],
                "ref": pick("[data-ref]"),
                "status": pick("[data-status]"),
                "balance": pick("[data-balance]"),
                "payments": payments,
            }

        try:
            return await retry(f"client {link['id']}", config["max_retry"], run)
        finally:
            await page.close()


async def main():
    os.makedirs("storage", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=config["headless"])
        pool = ProxyPool(config["proxy_file"])
        pool.load()
        proxy = pool.pick()

        ctx_args = {}
        if os.path.exists(STATE_PATH):
            ctx_args["storage_state"] = STATE_PATH
        pw_proxy = as_playwright_proxy(proxy)
        if pw_proxy:
            ctx_args["proxy"] = pw_proxy

        ctx = await browser.new_context(**ctx_args)
        page = await ctx.new_page()
        await login_if_needed(page)
        await ctx.storage_state(path=STATE_PATH)

        pace = Pace(config["req_per_sec"])
        links = await collect_links(page, pace)
        print(f"found {len(links)} clients")

        sem = asyncio.Semaphore(config["workers"])
        jobs = []
        for idx, link in enumerate(links, 1):
            print(f"[{idx}/{len(links)}] queued {link['id']} {link['name']}")
            jobs.append(scrape_one(ctx, link, sem, pace))

        rows = await asyncio.gather(*jobs)
        pool.ok(proxy)
        json_path, csv_path = save(config["out_dir"], rows)
        print(f"saved {json_path}")
        print(f"saved {csv_path}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
