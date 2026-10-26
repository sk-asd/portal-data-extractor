# Portal Data Extractor

Python scraping demo for authenticated portal style websites.

It runs against a local fake portal, not a real target. The point is to show the parts that usually matter in private scraping jobs: login, session reuse, paginated lists, detail pages, HTML parsing, retry, and structured exports.

## What it does

- logs in with Playwright
- saves and reuses browser session state
- collects client links from paginated tables
- opens detail pages in parallel
- optional proxy file hook
- basic pacing so requests do not all fire at once
- parses HTML with BeautifulSoup
- exports JSON and CSV
- includes a small local demo portal

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

If `python` opens the Microsoft Store or fails on Windows, use `py` instead:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m playwright install chromium
```

Start the demo portal:

```bash
python src/demo_portal.py
```

In another terminal:

```bash
python src/scraper.py
```

Demo login:

```text
demo / demo123
```

## Why no real target?

Real scraping work often includes private endpoints, account data, cookies, headers and customer-specific logic. None of that belongs in a public repo. This project keeps the target local and fake, while leaving the scraping workflow visible.

## Notes

If you want to try the proxy hook, create `proxies.txt` with one proxy per line. For the local demo you do not need it.
