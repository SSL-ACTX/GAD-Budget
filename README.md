# GAD Budget Monitoring (Web App)

Simple Gender and Development (GAD) Budget Monitoring web application using **Flask + SQLite**.

## Pages

- **Welcome**: introduction + navigation
- **Dashboard**: totals + category chart + recent items
- **Tables**: add/edit/delete + filters

## Run (Windows PowerShell)

```powershell
cd "C:\Users\Admin\Desktop\GAD Budget"
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python .\app.py
```

Then open `http://127.0.0.1:5000/`.

## Data

The app creates a local SQLite file on first run:

- `gad_budget.db`

It also inserts a few sample rows if the table is empty.
