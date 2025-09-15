# src/market_report/providers/nse.py
from typing import List, Dict, Any
from nsetools import Nse

def _normalize_item(item: dict) -> dict:
    # nsetools returns keys like 'symbol', 'ltp', 'previousPrice', 'netPrice', 'tradedQuantity'
    return {
        "symbol": item.get("symbol"),
        "name": item.get("symbol"),
        "ltp": item.get("ltp"),
        "previous_close": item.get("previousPrice"),
        "net_change": item.get("netPrice"),
        "traded_quantity": item.get("tradedQuantity"),
        "turnover_in_lakhs": item.get("turnoverInLakhs"),
        "source": "nsetools"
    }

import yfinance as yf

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
            pct_change = ((latest - prev) / prev) * 100

            results.append({
                "symbol": t.replace(".NS", ""),  # cleaner name
                "ltp": round(latest, 2),
                "net_change": round(net_change, 2),
                # remove traded_quantity since not needed
            })
        except Exception:
            continue

    sorted_res = sorted(results, key=lambda x: x["net_change"], reverse=True)
    return {
        "top_gainers": sorted_res[:limit],
        "top_losers": sorted_res[-limit:]
    }
