# src/prepare_report.py
from __future__ import annotations
import json, datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def load_latest_raw() -> Dict[str, Any]:
    files = sorted(RAW_DIR.glob("markets_*.json"))
    if not files:
        raise FileNotFoundError("No raw JSON files found.")
    latest = files[-1]
    print(f"[INFO] Using raw file: {latest.name}")
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_number(x):
    try:
        return float(x)
    except Exception:
        return None

def process(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    sections = snapshot.get("sections", {})

    # Normalize top gainers / losers
    for key in ["top_gainers", "top_losers"]:
        clean_list = []
        for row in sections.get(key, []):
            clean_list.append({
                "symbol": row.get("symbol", "N/A"),
                "ltp": normalize_number(row.get("ltp")),
                "net_change": normalize_number(row.get("net_change")),
                "traded_quantity": normalize_number(row.get("traded_quantity")),
            })
        sections[key] = clean_list

    snapshot["sections"] = sections
    return snapshot

def save(snapshot: Dict[str, Any]):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save JSON
    out_json = PROCESSED_DIR / "markets_latest.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"[OK] Wrote processed JSON: {out_json}")

    # Save Excel
    out_xlsx = PROCESSED_DIR / "markets_latest.xlsx"
    writer = pd.ExcelWriter(out_xlsx, engine="openpyxl")
    for name, items in snapshot.get("sections", {}).items():
        if isinstance(items, list) and items:
            df = pd.DataFrame(items)
            df.to_excel(writer, sheet_name=name[:30], index=False)
    writer.close()
    print(f"[OK] Wrote Excel: {out_xlsx}")


def main():
    snapshot = load_latest_raw()
    snapshot = process(snapshot)
    save(snapshot)

    # Summary
    sections = snapshot.get("sections", {})
    print("\n=== Processed summary ===")
    for k, v in sections.items():
        if isinstance(v, list):
            print(f"- {k}: {len(v)}")
    print("=========================")

if __name__ == "__main__":
    main()
