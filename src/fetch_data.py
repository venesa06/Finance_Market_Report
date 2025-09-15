# src/fetch_data.py
from __future__ import annotations
import json, pathlib, datetime
from typing import Dict, Any
import yaml
import yfinance as yf

from market_report.providers.yahoo import fetch_section
from market_report.providers.news import fetch_news

import requests

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
CONFIG_FILE = BASE_DIR / "config" / "tickers.yaml"
OUTPUT_DIR = BASE_DIR / "data" / "raw"


# ------------------ Config Loader ------------------
def load_config() -> Dict[str, Any]:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ------------------ Save JSON ------------------
def write_json(data: Dict[str, Any], outpath: pathlib.Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
# ------------------ Save CSV ------------------
import pandas as pd

def write_csv_sections(snapshot: Dict[str, Any], outdir: pathlib.Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    sections = snapshot.get("sections", {})

    for name, data in sections.items():
        if isinstance(data, list) and data:  # tabular data
            df = pd.DataFrame(data)
            df.to_csv(outdir / f"{name}.csv", index=False, encoding="utf-8")
        elif isinstance(data, dict) and data:  # e.g., fii_dii
            df = pd.DataFrame([data])
            df.to_csv(outdir / f"{name}.csv", index=False, encoding="utf-8")


# ------------------ Top Gainers & Losers ------------------
def fetch_top_gainers_and_losers(limit=5):
    tickers = [
        "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "ICICIBANK.NS",
        "SBIN.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS"
    ]

    data = yf.download(tickers, period="2d", interval="1d", group_by="ticker", progress=False)
    results = []

    for t in tickers:
        try:
            prev = float(data[t]["Close"].iloc[-2])
            latest = float(data[t]["Close"].iloc[-1])
            net_change = latest - prev

            results.append({
                "symbol": t.replace(".NS", ""),  # cleaner symbol
                "ltp": round(latest, 2),
                "net_change": round(net_change, 2)
            })
        except Exception:
            continue

    sorted_res = sorted(results, key=lambda x: x["net_change"], reverse=True)
    return {
        "top_gainers": sorted_res[:limit],
        "top_losers": sorted_res[-limit:]
    }


# ------------------ Commodities ------------------
def fetch_yf_data(symbols: list[dict]) -> list[dict]:
    results = []
    if not symbols:
        return results

    for item in symbols:
        symbol = item.get("symbol")
        name = item.get("name", symbol)
        try:
            df = yf.download(symbol, period="2d", interval="1d", progress=False)
            if not df.empty:
                close = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2]) if len(df) > 1 else close
                #close = float(df["Close"].iloc[-1].item())
                #prev = float(df["Close"].iloc[-2].item()) if len(df) > 1 else close

                pct_change = ((close - prev) / prev * 100) if prev else 0.0

                results.append({
                    "symbol": symbol,
                    "name": name,
                    "close": round(close, 2),
                    "pct_change": round(pct_change, 2)
                })
            else:
                results.append({"symbol": symbol, "name": name, "close": None, "pct_change": None})
        except Exception as e:
            print(f"[WARN] Failed to fetch {symbol}: {e}")
            results.append({"symbol": symbol, "name": name, "close": None, "pct_change": None})

    return results


# ------------------ FII/DII Activity ------------------
def fetch_fii_dii_activity():
    import requests, datetime, json, pathlib

    cache_file = OUTPUT_DIR / "fii_dii_cache.json"
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/"
    }

    try:
        session = requests.Session()
        resp = session.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and data:
            latest = data[0]
            fii_val = latest.get("FII_net", 0)
            dii_val = latest.get("DII_net", 0)
            date_val = latest.get("date", "N/A")

            result = {
                "date": date_val,
                "fii_value": fii_val,
                "dii_value": dii_val
            }

            # save to cache
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            return result

    except Exception as e:
        print(f"[WARN] Failed to fetch FII/DII data: {e}")

    # fallback: use cache if exists
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"note": "No FII/DII data available"}


# ------------------ Main ------------------
def main() -> None:
    cfg = load_config()

    snapshot: Dict[str, Any] = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sections": {}
    }

    # Task 1 — Indices, currencies, crypto
    sections = [
        ("indian_indices", cfg.get("indian_indices", [])),
        ("international_indices", cfg.get("international_indices", [])),
        ("currencies", cfg.get("currencies", [])),
        ("crypto", cfg.get("crypto", [])),
    ]

    for name, items in sections:
        print(f"[INFO] Fetching {name} …")
        snapshot["sections"][name] = fetch_section(name, items)

    # Task 2 — Top gainers/losers
    print("[INFO] Fetching top gainers & losers (NSE) …")
    gainer_loser = fetch_top_gainers_and_losers(limit=5)
    snapshot["sections"]["top_gainers"] = gainer_loser.get("top_gainers", [])
    snapshot["sections"]["top_losers"] = gainer_loser.get("top_losers", [])

    # Task 3 — News headlines
    print("[INFO] Fetching news headlines …")
    news = fetch_news(q="finance", page_size=6)
    snapshot["sections"]["news"] = news

    # Task 4 — Commodities
    print("[INFO] Fetching commodities …")
    commodities = fetch_yf_data(cfg.get("commodities", []))
    snapshot["sections"]["commodities"] = commodities

    # Task 5 — FII/DII Activity
    print("[INFO] Fetching FII/DII activity …")
    snapshot["sections"]["fii_dii"] = fetch_fii_dii_activity()

    # Save snapshot at the very end
    date_tag = datetime.date.today().strftime("%Y-%m-%d")

    # JSON
    outfile = OUTPUT_DIR / f"markets_{date_tag}.json"
    write_json(snapshot, outfile)
    print(f"[OK] Wrote JSON: {outfile}")

    # ------------------ Export CSVs for Power BI ------------------
    csv_dir = OUTPUT_DIR / f"csv_{date_tag}"
    write_csv_sections(snapshot, csv_dir)
    print(f"[OK] Wrote CSVs to: {csv_dir}")
    
    ##
    # place after you build the snapshot object, before exit
    csv_latest = OUTPUT_DIR / "csv_latest"
    csv_latest.mkdir(parents=True, exist_ok=True)

    for section, data in snapshot["sections"].items():
        if isinstance(data, list) and data:
            pd.DataFrame(data).to_csv(csv_latest / f"{section}.csv", index=False, encoding="utf-8")
        elif isinstance(data, dict) and data:
            # single-row summary e.g. fii_dii
            pd.DataFrame([data]).to_csv(csv_latest / f"{section}.csv", index=False, encoding="utf-8")
    ##

if __name__ == "__main__":
    main()
