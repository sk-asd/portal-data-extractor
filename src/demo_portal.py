from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


PORT = 4188
TOKEN = "demo-session"

clients = []
names = ["Atlas Market", "Nova Logistics", "Blue Finch", "Riverbyte", "Northwind"]
for i in range(17):
    clients.append({
        "id": f"C-{i + 1:04d}",
        "name": f"{names[i % len(names)]} {i + 1}",
        "ref": f"REF-{8900 + i}",
        "status": "review" if i % 6 == 0 else "late" if i % 4 == 0 else "ok",
        "balance": f"{1200 + i * 173:,}.00",
    })


def page(body):
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Demo Portal</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 32px auto; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    input, button {{ padding: 8px; margin: 4px 0; }}
    .pill {{ padding: 2px 8px; background: #eee; border-radius: 16px; }}
  </style>
</head>
<body>{body}</body>
</html>"""


def login(msg=""):
    warn = f"<p style='color:#b00020'>{msg}</p>" if msg else ""
    return page(f"""
      <h1>Demo client portal</h1>
      {warn}
      <form method="post" action="/login">
        <div><input name="user" placeholder="user"></div>
        <div><input name="pass" placeholder="pass" type="password"></div>
        <button>sign in</button>
      </form>
    """)


def list_page(page_no):
    per = 6
    start = (page_no - 1) * per
    part = clients[start:start + per]
    rows = "\n".join([
        f"<tr><td>{c['id']}</td><td>{c['name']}</td><td><a href='/client/{c['id']}'>open</a></td></tr>"
        for c in part
    ])
    nxt = f"<a class='next' href='/clients?page={page_no + 1}'>next</a>" if start + per < len(clients) else ""
    return page(f"""
      <h1>Clients</h1>
      <table class="clients">
        <thead><tr><th>id</th><th>name</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <p>{nxt}</p>
    """)


def client_page(client_id):
    c = next((x for x in clients if x["id"] == client_id), None)
    if not c:
        return page("<h1>missing</h1>")

    payments = "\n".join([
        f"<tr><td>2026-0{i + 4}-15</td><td>{'manual adjustment' if i == 2 else 'card payment'}</td><td>{180 + i * 65:.2f}</td></tr>"
        for i in range(3)
    ])

    return page(f"""
      <p><a href="/clients">back</a></p>
      <section data-client="{c['id']}">
        <h1 data-name>{c['name']}</h1>
        <p>Reference: <span data-ref>{c['ref']}</span></p>
        <p>Status: <span data-status class="pill">{c['status']}</span></p>
        <p>Balance: <span data-balance>{c['balance']}</span></p>
      </section>
      <h2>Payments</h2>
      <table class="payments">
        <thead><tr><th>date</th><th>desc</th><th>amount</th></tr></thead>
        <tbody>{payments}</tbody>
      </table>
    """)


class Handler(BaseHTTPRequestHandler):
    def send_html(self, status, body, headers=None):
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def logged(self):
        return f"portal={TOKEN}" in (self.headers.get("cookie") or "")

    def do_GET(self):
        url = urlparse(self.path)

        if url.path == "/login":
            return self.send_html(200, login())

        if not self.logged():
            return self.send_html(302, "", {"location": "/login"})

        if url.path == "/clients":
            q = parse_qs(url.query)
            page_no = int(q.get("page", ["1"])[0])
            return self.send_html(200, list_page(page_no))

        if url.path.startswith("/client/"):
            return self.send_html(200, client_page(url.path.rsplit("/", 1)[-1]))

        self.send_html(404, page("<h1>not found</h1>"))

    def do_POST(self):
        if self.path != "/login":
            return self.send_html(404, page("<h1>not found</h1>"))

        size = int(self.headers.get("content-length", 0))
        data = parse_qs(self.rfile.read(size).decode("utf-8"))
        if data.get("user", [""])[0] == "demo" and data.get("pass", [""])[0] == "demo123":
            return self.send_html(302, "", {
                "location": "/clients",
                "set-cookie": f"portal={TOKEN}; Path=/; HttpOnly",
            })
        self.send_html(401, login("bad login"))


if __name__ == "__main__":
    print(f"demo portal running on http://127.0.0.1:{PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
