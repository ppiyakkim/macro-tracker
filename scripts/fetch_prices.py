#!/usr/bin/env python3
import json, os, sys, time, urllib.request
from datetime import date, datetime, timezone, timedelta

INDICES = [
    {"id": "DJI",   "name": "Dow Jones",       "symbol": "%5EDJI"},
    {"id": "SPX",   "name": "S&P 500",         "symbol": "%5EGSPC"},
    {"id": "FTSE",  "name": "FTSE 100",        "symbol": "%5EFTSE"},
    {"id": "STOXX", "name": "Euro Stoxx 50",   "symbol": "%5ESTOXX50E"},
    {"id": "N225",  "name": "Nikkei 225",      "symbol": "%5EN225"},
    {"id": "HSI",   "name": "Hang Seng",       "symbol": "%5EHSI"},
    {"id": "KS11",  "name": "KOSPI",           "symbol": "%5EKS11"},
    {"id": "BVSP",  "name": "Bovespa",         "symbol": "%5EBVSP"},
    {"id": "XU100", "name": "BIST 100",        "symbol": "XU100.IS"},
    {"id": "NSEI",  "name": "Nifty 50",        "symbol": "%5ENSEI"},
    {"id": "SET",   "name": "SET",             "symbol": "%5ESET.BK"},
    {"id": "TWII",  "name": "Taiwan Weighted", "symbol": "%5ETWII"},
    {"id": "TA35",  "name": "TA-35",           "symbol": "TA35.TA"},
    {"id": "GC",    "name": "Gold Futures",    "symbol": "GC%3DF"},
    {"id": "CL",    "name": "Crude Oil",       "symbol": "CL%3DF"},
]

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "prices.json")

def date_to_ts(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())

def fetch_close_for_date(symbol: str, target: date) -> float | None:
    t1 = date_to_ts(target - timedelta(days=4))
    t2 = date_to_ts(target + timedelta(days=2))
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?interval=1d&period1={t1}&period2={t2}"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; macro-tracker/1.0)",
        "Accept": "application/json",
    }
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            result = data.get("chart", {}).get("result", [None])[0]
            if not result:
                return None
            timestamps = result.get("timestamp", [])
            closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            if not timestamps or not closes:
                return None
            target_ts = date_to_ts(target) + 86400
            best_price, best_ts = None, None
            for ts, close in zip(timestamps, closes):
                if close is None:
                    continue
                if ts <= target_ts:
                    if best_ts is None or ts > best_ts:
                        best_ts = ts
                        best_price = close
            if best_price is not None:
                return round(float(best_price), 2)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed for {symbol}: {e}")
            time.sleep(2 ** attempt)
    return None

def load_data() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: dict):
    data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {DATA_FILE}")

def main():
    target_str = os.environ.get("DATE") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target = date.fromisoformat(target_str)
    force = os.environ.get("FORCE", "").lower() in ("true", "1", "yes")

    print(f"\n{'='*50}")
    print(f"  Fetching prices for: {target_str} ({target.strftime('%a')})")
    print(f"{'='*50}")

    data = load_data()
    if "days" not in data:
        data["days"] = {}

    day_data = data["days"].get(target_str, {})
    fetched, failed, skipped = 0, 0, 0

    for idx in INDICES:
        iid = idx["id"]
        if iid in day_data and not force:
            print(f"  ⏭  {idx['name']:20s} already exists: {day_data[iid]}")
            skipped += 1
            continue
        print(f"  ↓  {idx['name']:20s} ({idx['symbol']}) ... ", end="", flush=True)
        price = fetch_close_for_date(idx["symbol"], target)
        if price is not None:
            day_data[iid] = price
            print(f"{price:>14,.2f}")
            fetched += 1
        else:
            print("FAILED")
            failed += 1
        time.sleep(0.4)

    if day_data:
        data["days"][target_str] = day_data
        save_data(data)

    print(f"\n  Result: {fetched} fetched, {skipped} skipped, {failed} failed")
    print(f"  Total days in dataset: {len(data['days'])}")

    if failed > 0 and fetched == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
