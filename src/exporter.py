import csv
import json
import os
from datetime import datetime


def save(out_dir, rows):
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.utcnow().isoformat(timespec="seconds").replace(":", "-")
    json_path = os.path.join(out_dir, f"clients-{stamp}.json")
    csv_path = os.path.join(out_dir, f"clients-{stamp}.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "name", "ref", "status", "balance", "last_payment"],
        )
        writer.writeheader()
        for r in rows:
            payments = r.get("payments") or []
            writer.writerow({
                "id": r.get("id", ""),
                "name": r.get("name", ""),
                "ref": r.get("ref", ""),
                "status": r.get("status", ""),
                "balance": r.get("balance", ""),
                "last_payment": payments[-1]["date"] if payments else "",
            })

    return json_path, csv_path
