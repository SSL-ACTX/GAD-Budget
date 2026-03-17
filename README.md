# GAD Budget Monitoring (Web App)

Simple Gender and Development (GAD) Budget Monitoring web application using **Flask + SQLite**.

## Pages

- **Welcome**: introduction + navigation
- **Dashboard**: totals + category chart + recent items
- **Tables**: add/edit/delete + filters
- **Summary**: office-level + grand totals
- **Expenditures**: object of expenditure breakdown (LBP2)
- **AIP Programs**: AIP program list with budgets (LBP4)

## Google Sheets Integration

This app can **two-way sync** with a Google Spreadsheet:

- **Spreadsheet**: https://docs.google.com/spreadsheets/d/1i5lppsscqkwMzUo1heUtPBxCiJmvFv6zD1SO6KY0HhA
- **Tabs synced**:
  - **LBP1** (Monitoring) ←→ SQLite `budgets` table
  - **SUMMARY** → SQLite `office_summary` + `grand_totals` (read-only)
  - **LBP2-Accounts** → SQLite `expenditures` (read-only)
  - **LBP4-AIP-Obligated** → SQLite `aip_programs` (read-only)

### Setup Google Sheets Access

1. **Create a Google Cloud project**
   - Go to https://console.cloud.google.com/
   - Create a new project (e.g., "GAD Budget Sync")

2. **Enable the Google Sheets and Google Drive APIs**
   - APIs & Services → Library
   - Enable both "Google Sheets API" and "Google Drive API"

3. **Create a Service Account**
   - IAM & Admin → Service Accounts → Create Service Account
   - Give it a name (e.g., "gad-sync")
   - Grant it "Editor" role
   - Create and download a JSON key file

4. **Save the credentials**
   - Rename the downloaded JSON file to `credentials.json`
   - Place it in the project root (same folder as `app.py`)

5. **Share the spreadsheet**
   - Open the Google Spreadsheet: https://docs.google.com/spreadsheets/d/1i5lppsscqkwMzUo1heUtPBxCiJmvFv6zD1SO6KY0HhA
   - Click Share → Add the service account email (e.g., `gad-sync@YOUR_PROJECT_ID.iam.gserviceaccount.com`)
   - Give it **Editor** access

### Running the App

```powershell
# Windows PowerShell
cd "C:\Users\Admin\Desktop\GAD Budget"
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000/`.

### Syncing Data

- Click the **"Sync with Sheets"** button in the navigation bar to pull all data from Google Sheets and push local changes back.
- When you add, edit, or delete a record in the app, it will automatically try to sync that change to Google Sheets.
- If sync fails, you'll see a warning message but the data is still saved locally.

## Data

The app creates a local SQLite file on first run:

- `gad_budget.db`

It also inserts a few sample rows if the table is empty.

## Environment Variables (optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CREDENTIALS_JSON` | Path to service account JSON | `credentials.json` |
| `SPREADSHEET_ID` | Override Google Sheets ID | `1i5lppsscqkwMzUo1heUtPBxCiJmvFv6zD1SO6KY0HhA` |
| `FLASK_SECRET_KEY` | Flask secret key | `dev-secret-change-me` |
