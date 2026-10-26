import os


def bool_env(name, default):
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() not in ("0", "false", "no")


def int_env(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


config = {
    "base_url": os.getenv("BASE_URL", "http://127.0.0.1:4188"),
    "user": os.getenv("PORTAL_USER", "demo"),
    "pass": os.getenv("PORTAL_PASS", "demo123"),
    "headless": bool_env("HEADLESS", True),
    "workers": int_env("WORKERS", 3),
    "max_retry": int_env("MAX_RETRY", 3),
    "out_dir": os.getenv("OUT_DIR", "out"),
    "proxy_file": os.getenv("PROXY_FILE", "proxies.txt"),
    "req_per_sec": int_env("REQ_PER_SEC", 2),
}
