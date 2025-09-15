## Finance Market Report

An automated pipeline to fetch, process, and generate daily financial market reports in PDF & CSV formats.
The report includes Indian & International indices, currencies, commodities, crypto, top gainers/losers, Market Mood Index (MMI), FII/DII activity, and curated news.

## Features

📈 Candlestick charts for indices & commodities

💹 Top Gainers/Losers with net change values

🪙 Currencies & Crypto performance

📰 Market news headlines (auto-fetched)

😃 Market Mood Index (MMI) gauge

🏦 FII/DII activity (latest available data)

📑 PDF report generation (newspaper-like layout, ≤7 pages)

🔄 CSV exports (ready for Power BI or Excel analysis)

## Project Structure
Finance_Market_Report/
│── config/               # Configuration (tickers.yaml)
│── data/
│   ├── raw/              # JSON + CSV snapshots
│   └── processed/        # Prepared data for report
│── reports/              # Generated PDF reports
│── src/
│   ├── fetch_data.py     # Fetch all market data
│   ├── prepare_report.py # Clean & process snapshot
│   ├── generate_report.py# Build PDF reports
│   └── market_report/    # Providers (Yahoo, NSE, News, FII/DII)
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│── .gitignore


## Setup & Installation

# Clone the repo

git clone https://github.com/venesa06/Finance_Market_Report.git
cd Finance_Market_Report


# Create virtual environment

python -m venv .venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows


# Install dependencies

pip install -r requirements.txt

## Usage
# Fetch fresh data

python src/fetch_data.py


→ Saves JSON + CSV snapshots in data/raw/

# Prepare processed data

python src/prepare_report.py


→ Cleans & merges data → saves in data/processed/

# Generate PDF report

python src/generate_report.py


→ Creates a PDF in reports/

## Tech Stack

Python 3.11+

yfinance
 – Market data

ReportLab
 – PDF generation

matplotlib
 & mplfinance
 – Charts

pandas
 – Data wrangling

## Summary
# Market Report Starter (Task 1 + Task 2)

## How to run (Windows PowerShell)
1. Extract the ZIP somewhere, e.g. `C:\Users\Shree\Downloads\market_report_starter`
2. Open PowerShell in that folder, then run:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python src/fetch_data.py
   ```
   If activation is blocked:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   .\.venv\Scripts\Activate.ps1
   ```

## Output
The script writes a JSON snapshot to `data/raw/markets_<YYYY-MM-DD>.json`. The folder is auto-created.

Open it with:
```powershell
notepad data\raw\markets_YYYY-MM-DD.json
```

## Secrets
`.env` contains `NEWSAPI_KEY`. Do NOT commit `.env` to git.


