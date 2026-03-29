#!/usr/bin/env python3
import os, subprocess, sys, time
from datetime import date, timedelta

def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    if s.lower() in ("", "none", "null", "undefined"):
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None

START = parse_date(os.environ.get("START_DATE")) or \
        (parse_date(sys.argv[1]) if len(sys.argv) >= 2 else None) or \
        date(2026, 1, 1)

END = parse_date(os.environ.get("END_DATE")) or \
      (parse_date(sys.argv[2]) if len(sys.argv) >= 3 else None) or \
      date.today()

print(f"Backfill: {START} -> {END}")
total = sum(1 for i in range((END - START).days + 1)
            if (START + timedelta(days=i)).weekday() < 5)
print(f"Trading days: ~{total}\n")

script = os.path.join(os.path.dirname(__file__), "fetch_prices.py")
success, failed = [], []

current = START
while current <= END:
    if current.weekday() < 5:
        env = os.environ.copy()
        env["DATE"] = current.isoformat()
        result = subprocess.run([sys.executable, script], env=env)
        if result.returncode == 0:
            success.append(current.isoformat())
        else:
            failed.append(current.isoformat())
        time.sleep(1.0)
    current += timedelta(days=1)

print(f"\nDone: {len(success)} fetched, {len(failed)} failed")
if failed:
    print(f"Failed: {', '.join(failed)}")
if failed and not success:
    sys.exit(1)
