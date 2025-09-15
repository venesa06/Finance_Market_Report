import requests, datetime

NSE_FII_DII_URL = "https://www.nseindia.com/api/fiidiiTradeReact"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/"
}

def fetch_fii_dii_activity():
    try:
        session = requests.Session()
        resp = session.get(NSE_FII_DII_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list) or not data:
            return {}

        latest = data[0]  # first element is most recent

        return {
            "date": latest.get("date", datetime.date.today().strftime("%Y-%m-%d")),
            "fii_value": latest.get("FII_net", "0"),
            "dii_value": latest.get("DII_net", "0")
        }

    except Exception as e:
        print(f"[WARN] Failed to fetch FII/DII data: {e}")
        return {}
