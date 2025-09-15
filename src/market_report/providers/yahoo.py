# src/market_report/providers/yahoo.py
from typing import List, Dict, Any
import pandas as pd
import yfinance as yf

def _two_day_close(symbol: str):
    """Return (prev_close, last_close, last_date) or (None, None, None) if unavailable"""
    try:
        hist = yf.Ticker(symbol).history(period="10d", interval="1d", auto_adjust=False)
        if hist is None or hist.empty:
            return None, None, None
        hist = hist.dropna(subset=["Close"])
        if len(hist) < 2:
            return None, None, None
        last = hist.iloc[-1]
        prev = hist.iloc[-2]
        prev_close = float(prev["Close"])
        last_close = float(last["Close"])
        last_date = str(pd.to_datetime(last.name).date())
        return prev_close, last_close, last_date
    except Exception:
        return None, None, None

def fetch_section(section: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        sym = item.get("symbol")
        name = item.get("name", sym)
        prev_c, close_c, as_of = _two_day_close(sym)
        if prev_c is None or close_c is None:
            out.append({
                "section": section,
                "symbol": sym,
                "name": name,
                "as_of_date": None,
                "close": None,
                "prev_close": None,
                "pct_change": None,
                "source": "YahooFinance",
                "error": "No recent data"
            })
            continue
        pct = None
        try:
            if prev_c != 0:
                pct = round((close_c - prev_c) / prev_c * 100.0, 2)
        except Exception:
            pct = None

        out.append({
            "section": section,
            "symbol": sym,
            "name": name,
            "as_of_date": as_of,
            "close": round(close_c, 2),
            "prev_close": round(prev_c, 2),
            "pct_change": pct,
            "source": "YahooFinance",
        })
    return out
