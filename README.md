
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
