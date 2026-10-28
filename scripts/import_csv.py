import argparse
import csv
import json
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/listings/bulk"
FIELDS = ["business_name", "category", "city", "address", "phone", "source"]

def main():
    parser = argparse.ArgumentParser(description="Import a CSV file into the Business Listings API.")
    parser.add_argument("--csv", required=True, help="Path to CSV containing required listing fields.")
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument("--url", default=API_URL)
    args = parser.parse_args()
    if args.batch_size < 1 or args.batch_size > 5000:
        parser.error("--batch-size must be between 1 and 5000")
    path = Path(args.csv)
    if not path.exists():
        raise SystemExit(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [{k: (row.get(k) or "").strip() or None for k in FIELDS} for row in csv.DictReader(f)]
    rows = [r for r in rows if r["business_name"] and r["category"] and r["city"] and r["source"]]
    if not rows:
        raise SystemExit("No valid rows found. Required: business_name, category, city, source.")
    inserted = 0
    for start in range(0, len(rows), args.batch_size):
        batch = rows[start:start + args.batch_size]
        body = json.dumps({"listings": batch}).encode("utf-8")
        req = urllib.request.Request(args.url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                inserted += result.get("inserted", 0)
                print(f"Batch {start // args.batch_size + 1}: inserted {result.get('inserted', 0)}")
        except urllib.error.HTTPError as exc:
            print(exc.read().decode("utf-8", errors="replace"))
            raise SystemExit(f"Import failed with HTTP {exc.code}")
        except urllib.error.URLError as exc:
            raise SystemExit(f"Could not reach API at {args.url}: {exc}")
    print(f"Done. Inserted {inserted} records.")

if __name__ == "__main__":
    main()
