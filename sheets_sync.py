"""
sheets_sync.py
==============
Two-way sync between the local SQLite database and the Google Spreadsheet:

  https://docs.google.com/spreadsheets/d/1i5lppsscqkwMzUo1heUtPBxCiJmvFv6zD1SO6KY0HhA

Tabs synced
-----------
  LBP1  ← → budgets          (Monitoring / transaction ledger)
  SUMMARY → office_summary + grand_totals  (read-only push from Sheets)
  LBP2  → expenditures       (read-only push from Sheets)
  LBP4  → aip_programs       (read-only push from Sheets)

Usage
-----
  from sheets_sync import SheetsSync
  sync = SheetsSync("credentials.json")
  result = sync.full_sync(db_path)   # pull all tabs, push monitoring rows

Environment / config
--------------------
  GOOGLE_CREDENTIALS_JSON  – path to service account JSON (default: credentials.json)
  SPREADSHEET_ID           – override sheet ID (optional)
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

SPREADSHEET_ID = os.environ.get(
    "SPREADSHEET_ID",
    "1i5lppsscqkwMzUo1heUtPBxCiJmvFv6zD1SO6KY0HhA",
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Sheet tab names — adjust if yours differ
TAB_MONITORING  = "LBP1"
TAB_SUMMARY     = "SUMMARY"
TAB_LBP2        = "LBP2-Accounts"
TAB_LBP4        = "LBP4-AIP-Obligated"

# Column header row in the Monitoring sheet (1-indexed row number in the sheet)
MONITORING_HEADER_ROW = 1

# Columns expected in the Monitoring tab (must match sheet order exactly)
MONITORING_COLS = [
    "no", "date", "office", "status", "particulars",
    "pow_title", "pow_date_of_activity", "reference_code",
    "ppa_allotted_budget", "ppa_description",
    "accounts", "account_code",
    "proposed_budget", "actual_obligation",
    "payee", "caf", "obligation_number",
    "venue_food_honorarium", "actual_remaining_budget",
    "remarks",
]

MONITORING_HEADER = [c.upper().replace("_", " ") for c in MONITORING_COLS]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_float(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace("₱", "").replace("-", "0")
    if not s or s in ("-", "—"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _connect(db_path: str) -> sqlite3.Connection:
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db


# ── Main class ────────────────────────────────────────────────────────────────

class SheetsSync:
    """Handles all read/write operations against the Google Spreadsheet."""

    def __init__(self, credentials_path: str | None = None):
        self._creds_path = (
            credentials_path
            or os.environ.get("GOOGLE_CREDENTIALS_JSON", "credentials.json")
        )
        self._gc = None  # lazy gspread client

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _client(self):
        """Return an authenticated gspread client (cached)."""
        if self._gc is not None:
            return self._gc

        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError as exc:
            raise RuntimeError(
                "gspread / google-auth not installed. "
                "Run: pip install gspread google-auth"
            ) from exc

        if not os.path.exists(self._creds_path):
            raise FileNotFoundError(
                f"Google credentials file not found: {self._creds_path!r}\n"
                "See README for setup instructions."
            )

        creds = Credentials.from_service_account_file(
            self._creds_path, scopes=SCOPES
        )
        self._gc = gspread.authorize(creds)
        return self._gc

    def _spreadsheet(self):
        return self._client().open_by_key(SPREADSHEET_ID)

    def _worksheet(self, tab_name: str):
        ss = self._spreadsheet()
        try:
            return ss.worksheet(tab_name)
        except Exception:
            # Try case-insensitive fallback
            for ws in ss.worksheets():
                if ws.title.lower() == tab_name.lower():
                    return ws
            raise

    # ── Full sync entry point ─────────────────────────────────────────────────

    def full_sync(self, db_path: str) -> dict[str, Any]:
        """
        Perform a full two-way sync:
          1. Pull Summary / LBP2 / LBP4 from Sheets → SQLite  (Sheets wins)
          2. Pull Monitoring from Sheets → merge into SQLite   (Sheets wins for existing rows)
          3. Push any SQLite-only Monitoring rows → Sheets     (SQLite wins for new rows)

        Returns a dict with counts/errors for each tab.
        """
        result: dict[str, Any] = {"ok": True, "tabs": {}, "timestamp": _iso_now()}

        try:
            result["tabs"]["summary"]      = self.pull_summary(db_path)
            result["tabs"]["expenditures"] = self.pull_lbp2(db_path)
            result["tabs"]["aip_programs"] = self.pull_lbp4(db_path)
            result["tabs"]["monitoring"]   = self.sync_monitoring(db_path)
        except Exception as exc:
            logger.exception("full_sync failed")
            result["ok"] = False
            result["error"] = str(exc)

        return result

    # ── Monitoring (LBP1) — two-way ───────────────────────────────────────────

    def sync_monitoring(self, db_path: str) -> dict[str, Any]:
        """
        Pull rows from the Monitoring sheet into SQLite, then push any
        SQLite rows that don't exist in Sheets back up.
        """
        ws = self._worksheet(TAB_MONITORING)
        all_values = ws.get_all_values()

        if not all_values:
            # Sheet is empty — write header + push all local rows
            self._ensure_monitoring_header(ws)
            pushed = self._push_all_monitoring(db_path, ws)
            return {"pulled": 0, "pushed": pushed, "note": "sheet was empty"}

        # Find header row
        header_row_idx, col_map = self._find_monitoring_header(all_values)
        if header_row_idx is None:
            # No recognisable header — initialise sheet
            self._ensure_monitoring_header(ws)
            pushed = self._push_all_monitoring(db_path, ws)
            return {"pulled": 0, "pushed": pushed, "note": "header not found, initialised sheet"}

        data_rows = all_values[header_row_idx + 1:]  # rows after header

        # Build set of obligation numbers already in sheet (used as natural key)
        sheet_obligation_numbers: set[str] = set()
        obl_idx = col_map.get("obligation_number")

        pulled = 0
        now = _iso_now()

        with _connect(db_path) as db:
            for raw in data_rows:
                row = self._map_monitoring_row(raw, col_map)
                if not row.get("office"):
                    continue  # skip blank rows

                obl_no = (row.get("obligation_number") or "").strip()
                if obl_idx is not None and obl_no:
                    sheet_obligation_numbers.add(obl_no)

                # Upsert by obligation_number (if present) else by no+date+office
                existing = None
                if obl_no:
                    cur = db.execute(
                        "SELECT id FROM budgets WHERE obligation_number = ?", [obl_no]
                    )
                    existing = cur.fetchone()

                if existing:
                    db.execute(
                        """
                        UPDATE budgets SET
                          no=?, date=?, office=?, status=?, particulars=?,
                          pow_title=?, pow_date_of_activity=?, reference_code=?,
                          ppa_allotted_budget=?, ppa_description=?,
                          accounts=?, account_code=?,
                          proposed_budget=?, actual_obligation=?,
                          payee=?, caf=?, obligation_number=?,
                          venue_food_honorarium=?, actual_remaining_budget=?,
                          remarks=?
                        WHERE id=?
                        """,
                        [
                            row.get("no"), row.get("date"), row.get("office"),
                            row.get("status", "Planned"), row.get("particulars"),
                            row.get("pow_title"), row.get("pow_date_of_activity"),
                            row.get("reference_code"),
                            _safe_float(row.get("ppa_allotted_budget")),
                            row.get("ppa_description"),
                            row.get("accounts"), row.get("account_code"),
                            _safe_float(row.get("proposed_budget")),
                            _safe_float(row.get("actual_obligation")),
                            row.get("payee"), row.get("caf"), obl_no,
                            row.get("venue_food_honorarium"),
                            _safe_float(row.get("actual_remaining_budget")),
                            row.get("remarks"),
                            existing["id"],
                        ],
                    )
                else:
                    db.execute(
                        """
                        INSERT INTO budgets (
                          no, date, office, status, particulars,
                          pow_title, pow_date_of_activity, reference_code,
                          ppa_allotted_budget, ppa_description,
                          accounts, account_code,
                          proposed_budget, actual_obligation,
                          payee, caf, obligation_number,
                          venue_food_honorarium, actual_remaining_budget,
                          remarks, created_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        [
                            row.get("no"), row.get("date"), row.get("office"),
                            row.get("status", "Planned"), row.get("particulars"),
                            row.get("pow_title"), row.get("pow_date_of_activity"),
                            row.get("reference_code"),
                            _safe_float(row.get("ppa_allotted_budget")),
                            row.get("ppa_description"),
                            row.get("accounts"), row.get("account_code"),
                            _safe_float(row.get("proposed_budget")),
                            _safe_float(row.get("actual_obligation")),
                            row.get("payee"), row.get("caf"), obl_no,
                            row.get("venue_food_honorarium"),
                            _safe_float(row.get("actual_remaining_budget")),
                            row.get("remarks"),
                            now,
                        ],
                    )
                    pulled += 1

            db.commit()

            # Push local rows whose obligation_number is not yet in Sheets
            local_rows = [
                dict(r)
                for r in db.execute(
                    """
                    SELECT * FROM budgets
                    WHERE obligation_number IS NOT NULL
                      AND obligation_number != ''
                    ORDER BY id ASC
                    """
                ).fetchall()
            ]

        rows_to_push = [
            r for r in local_rows
            if (r.get("obligation_number") or "").strip() not in sheet_obligation_numbers
        ]

        pushed = 0
        if rows_to_push:
            new_sheet_rows = [
                [str(r.get(col) or "") for col in MONITORING_COLS]
                for r in rows_to_push
            ]
            ws.append_rows(new_sheet_rows, value_input_option="USER_ENTERED")
            pushed = len(rows_to_push)

        return {"pulled": pulled, "pushed": pushed}

    # ── Push a single new budget row to Sheets ────────────────────────────────

    def push_budget_row(self, db_path: str, item_id: int) -> bool:
        """
        Called after add_item / update_item to reflect the change in Sheets.
        Returns True on success.
        """
        with _connect(db_path) as db:
            row = db.execute(
                "SELECT * FROM budgets WHERE id = ?", [item_id]
            ).fetchone()
            if not row:
                return False
            row = dict(row)

        try:
            ws = self._worksheet(TAB_MONITORING)
            all_values = ws.get_all_values()
            header_row_idx, col_map = self._find_monitoring_header(all_values)

            if header_row_idx is None:
                self._ensure_monitoring_header(ws)
                all_values = ws.get_all_values()
                header_row_idx, col_map = self._find_monitoring_header(all_values)

            obl_no = (row.get("obligation_number") or "").strip()

            # Try to find and update existing sheet row
            if obl_no and header_row_idx is not None:
                obl_col_idx = col_map.get("obligation_number")
                if obl_col_idx is not None:
                    for i, srow in enumerate(all_values[header_row_idx + 1:], start=header_row_idx + 2):
                        if len(srow) > obl_col_idx and srow[obl_col_idx].strip() == obl_no:
                            # Update entire row in place
                            new_row = [str(row.get(col) or "") for col in MONITORING_COLS]
                            col_letter_start = "A"
                            col_letter_end = chr(ord("A") + len(MONITORING_COLS) - 1)
                            ws.update(
                                f"{col_letter_start}{i}:{col_letter_end}{i}",
                                [new_row],
                                value_input_option="USER_ENTERED",
                            )
                            return True

            # Not found in sheet — append
            new_row = [str(row.get(col) or "") for col in MONITORING_COLS]
            ws.append_rows([new_row], value_input_option="USER_ENTERED")
            return True

        except Exception as exc:
            logger.warning("push_budget_row failed: %s", exc)
            return False

    def delete_budget_row(self, db_path: str, obligation_number: str) -> bool:
        """
        Remove the matching row from the Monitoring sheet by obligation_number.
        Returns True on success.
        """
        if not obligation_number:
            return False
        try:
            ws = self._worksheet(TAB_MONITORING)
            all_values = ws.get_all_values()
            header_row_idx, col_map = self._find_monitoring_header(all_values)
            if header_row_idx is None:
                return False

            obl_col_idx = col_map.get("obligation_number")
            if obl_col_idx is None:
                return False

            for i, srow in enumerate(all_values[header_row_idx + 1:], start=header_row_idx + 2):
                if len(srow) > obl_col_idx and srow[obl_col_idx].strip() == obligation_number.strip():
                    ws.delete_rows(i)
                    return True
        except Exception as exc:
            logger.warning("delete_budget_row failed: %s", exc)
        return False

    # ── Summary (read Sheets → SQLite) ────────────────────────────────────────

    def pull_summary(self, db_path: str) -> dict[str, Any]:
        ws = self._worksheet(TAB_SUMMARY)
        rows = ws.get_all_values()

        grand = {}
        offices = []

        # Parse grand totals from rows 2-5 (0-indexed: rows[1]-rows[4])
        # Structure mirrors sheet_analysis.txt
        if len(rows) > 2:
            r2 = rows[2]  # numeric grand-total row
            grand["total_gad_threshold"] = _safe_float(r2[0] if r2 else 0)
            grand["total_obligated"]     = _safe_float(r2[2] if len(r2) > 2 else 0)
            grand["total_earnmarked"]    = _safe_float(r2[3] if len(r2) > 3 else 0)
            grand["total_expenses"]      = _safe_float(r2[4] if len(r2) > 4 else 0)
            grand["utilization_pct"]     = _safe_float(r2[6] if len(r2) > 6 else 0)

        if len(rows) > 4:
            r4 = rows[4]  # PS/MOOE/CO breakdown
            grand["ps_expenses"]   = _safe_float(r4[0] if r4 else 0)
            grand["ps_balance"]    = _safe_float(r4[2] if len(r4) > 2 else 0)
            grand["mooe_expenses"] = _safe_float(r4[3] if len(r4) > 3 else 0)
            grand["mooe_balance"]  = _safe_float(r4[4] if len(r4) > 4 else 0)
            grand["co_expenses"]   = _safe_float(r4[5] if len(r4) > 5 else 0)
            grand["co_balance"]    = _safe_float(r4[6] if len(r4) > 6 else 0)

        # Office rows start at row index 6 (row 7 in sheet)
        for r in rows[6:]:
            if not r or not r[0] or r[0].strip() in ("", "ANCHORED\nOFFICES", "ANCHORED OFFICES"):
                continue
            offices.append({
                "office":           r[0].strip(),
                "budget_threshold": _safe_float(r[1] if len(r) > 1 else 0),
                "obligated":        _safe_float(r[2] if len(r) > 2 else 0),
                "earnmarked":       _safe_float(r[3] if len(r) > 3 else 0),
                "expenses":         _safe_float(r[4] if len(r) > 4 else 0),
                "balance":          _safe_float(r[5] if len(r) > 5 else 0),
                "utilization_pct":  _safe_float(r[6] if len(r) > 6 else 0),
            })

        with _connect(db_path) as db:
            # Upsert grand totals
            db.execute("DELETE FROM grand_totals")
            db.execute(
                """
                INSERT INTO grand_totals (
                  total_gad_threshold, total_obligated, total_earnmarked,
                  total_expenses, utilization_pct,
                  ps_expenses, ps_balance,
                  mooe_expenses, mooe_balance,
                  co_expenses, co_balance
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                [
                    grand.get("total_gad_threshold", 0),
                    grand.get("total_obligated", 0),
                    grand.get("total_earnmarked", 0),
                    grand.get("total_expenses", 0),
                    grand.get("utilization_pct", 0),
                    grand.get("ps_expenses", 0),
                    grand.get("ps_balance", 0),
                    grand.get("mooe_expenses", 0),
                    grand.get("mooe_balance", 0),
                    grand.get("co_expenses", 0),
                    grand.get("co_balance", 0),
                ],
            )

            # Upsert office summary
            db.execute("DELETE FROM office_summary")
            db.executemany(
                """
                INSERT INTO office_summary (
                  office, budget_threshold, obligated, earnmarked,
                  expenses, balance, utilization_pct
                ) VALUES (?,?,?,?,?,?,?)
                """,
                [
                    (
                        o["office"], o["budget_threshold"], o["obligated"],
                        o["earnmarked"], o["expenses"], o["balance"],
                        o["utilization_pct"],
                    )
                    for o in offices
                ],
            )
            db.commit()

        return {"offices": len(offices), "grand_updated": bool(grand)}

    # ── LBP2-Accounts (read Sheets → SQLite) ──────────────────────────────────

    def pull_lbp2(self, db_path: str) -> dict[str, Any]:
        ws = self._worksheet(TAB_LBP2)
        rows = ws.get_all_values()

        records = []
        for r in rows:
            if not r or not any(r):
                continue
            # Skip header rows (first cell is "No." or blank/non-numeric)
            no_val = r[0].strip()
            if not no_val or no_val.lower() in ("no.", "no", "#"):
                continue
            try:
                float(no_val)
            except ValueError:
                continue  # not a data row

            records.append({
                "no":               no_val,
                "object_name":      r[1].strip() if len(r) > 1 else "",
                "account_code":     r[2].strip() if len(r) > 2 else "",
                "allotted_budget":  _safe_float(r[3] if len(r) > 3 else 0),
                "earnmarked":       _safe_float(r[4] if len(r) > 4 else 0),
                "actual_obligated": _safe_float(r[5] if len(r) > 5 else 0),
                "expenses_total":   _safe_float(r[6] if len(r) > 6 else 0),
                "balance_budget":   _safe_float(r[7] if len(r) > 7 else 0),
            })

        with _connect(db_path) as db:
            db.execute("DELETE FROM expenditures")
            db.executemany(
                """
                INSERT INTO expenditures (
                  no, object_name, account_code, allotted_budget,
                  earnmarked, actual_obligated, expenses_total, balance_budget
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                [
                    (
                        r["no"], r["object_name"], r["account_code"],
                        r["allotted_budget"], r["earnmarked"],
                        r["actual_obligated"], r["expenses_total"],
                        r["balance_budget"],
                    )
                    for r in records
                ],
            )
            db.commit()

        return {"rows": len(records)}

    # ── LBP4-AIP-Obligated (read Sheets → SQLite) ─────────────────────────────

    def pull_lbp4(self, db_path: str) -> dict[str, Any]:
        ws = self._worksheet(TAB_LBP4)
        rows = ws.get_all_values()

        records = []
        # Data rows start after the multi-row header (typically row index 8+)
        # We detect data rows by: col 0 has a ref_code OR col 2 has a description
        header_passed = False
        for r in rows:
            if not r or not any(r):
                continue
            ref    = r[0].strip() if r else ""
            office = r[1].strip() if len(r) > 1 else ""
            desc   = r[2].strip() if len(r) > 2 else ""

            if not desc:
                continue

            # Detect the divider rows that signal header is done
            if ref in ("A I P Ref. Code",) or desc in (
                "PROGRAM / PROJECT / ACTIVITY DESCRIPTION",
                "( P S )",
            ):
                header_passed = True
                continue

            if not header_passed:
                # Check if this looks like actual data (has numeric budget col)
                total_val = r[6].strip() if len(r) > 6 else ""
                if not total_val:
                    # Might be a section header — treat as header row
                    records.append({
                        "ref_code": ref or None,
                        "office": office or None,
                        "description": desc,
                        "ps_budget": 0, "mooe_budget": 0, "co_budget": 0,
                        "total_budget": 0, "earnmarked": 0,
                        "obligated": 0, "expenses": 0, "balance": 0,
                        "status": None, "utilization_pct": 0,
                        "quarterly_schedule": None,
                        "is_header": 1,
                    })
                    continue

            # Determine if header row (no numeric data)
            ps_val   = r[3].strip() if len(r) > 3 else ""
            total_v  = r[6].strip() if len(r) > 6 else ""
            is_hdr   = 0

            try:
                float(total_v.replace(",", "")) if total_v and total_v != "-" else None
            except ValueError:
                is_hdr = 1

            if not total_v or total_v in ("-", ""):
                is_hdr = 1

            records.append({
                "ref_code":          ref or None,
                "office":            office or None,
                "description":       desc,
                "ps_budget":         _safe_float(ps_val),
                "mooe_budget":       _safe_float(r[4] if len(r) > 4 else 0),
                "co_budget":         _safe_float(r[5] if len(r) > 5 else 0),
                "total_budget":      _safe_float(r[6] if len(r) > 6 else 0),
                "earnmarked":        _safe_float(r[7] if len(r) > 7 else 0),
                "obligated":         _safe_float(r[8] if len(r) > 8 else 0),
                "expenses":          _safe_float(r[9] if len(r) > 9 else 0),
                "balance":           _safe_float(r[10] if len(r) > 10 else 0),
                "status":            r[11].strip() if len(r) > 11 else None,
                "utilization_pct":   _safe_float(r[12] if len(r) > 12 else 0),
                "quarterly_schedule": r[13].strip() if len(r) > 13 else None,
                "is_header":         is_hdr,
            })

        with _connect(db_path) as db:
            db.execute("DELETE FROM aip_programs")
            db.executemany(
                """
                INSERT INTO aip_programs (
                  ref_code, office, description,
                  ps_budget, mooe_budget, co_budget, total_budget,
                  earnmarked, obligated, expenses, balance,
                  status, utilization_pct, quarterly_schedule, is_header
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                [
                    (
                        r["ref_code"], r["office"], r["description"],
                        r["ps_budget"], r["mooe_budget"], r["co_budget"],
                        r["total_budget"], r["earnmarked"], r["obligated"],
                        r["expenses"], r["balance"], r["status"],
                        r["utilization_pct"], r["quarterly_schedule"],
                        r["is_header"],
                    )
                    for r in records
                ],
            )
            db.commit()

        return {"rows": len(records)}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _find_monitoring_header(
        self, all_values: list[list[str]]
    ) -> tuple[int | None, dict[str, int]]:
        """
        Search for the header row in the Monitoring sheet.
        Returns (row_index, {field_name: col_index}).
        """
        for idx, row in enumerate(all_values):
            normalised = [c.strip().lower().replace(" ", "_") for c in row]
            if "office" in normalised and "obligation_number" in normalised:
                col_map = {}
                for field in MONITORING_COLS:
                    # Try exact match first
                    try:
                        col_map[field] = normalised.index(field)
                    except ValueError:
                        # Try the uppercase display header
                        display = field.upper().replace("_", " ").lower().replace(" ", "_")
                        try:
                            col_map[field] = normalised.index(display)
                        except ValueError:
                            pass
                return idx, col_map
        return None, {}

    def _ensure_monitoring_header(self, ws) -> None:
        """Write the header row to row 1 of the Monitoring sheet if empty."""
        existing = ws.row_values(1)
        if not any(existing):
            ws.update("A1", [MONITORING_HEADER], value_input_option="USER_ENTERED")

    def _push_all_monitoring(self, db_path: str, ws) -> int:
        """Push all local budget rows to an empty Monitoring sheet."""
        with _connect(db_path) as db:
            rows = [dict(r) for r in db.execute(
                "SELECT * FROM budgets ORDER BY id ASC"
            ).fetchall()]

        if not rows:
            return 0

        sheet_rows = [
            [str(r.get(col) or "") for col in MONITORING_COLS]
            for r in rows
        ]
        ws.append_rows(sheet_rows, value_input_option="USER_ENTERED")
        return len(sheet_rows)

    def _map_monitoring_row(
        self, raw: list[str], col_map: dict[str, int]
    ) -> dict[str, Any]:
        """Map a raw sheet row to a budget dict using the column map."""
        def _get(field: str) -> str:
            idx = col_map.get(field)
            if idx is None or idx >= len(raw):
                return ""
            return raw[idx].strip()

        return {f: _get(f) for f in MONITORING_COLS}


# ── Module-level convenience ──────────────────────────────────────────────────

def get_sync(credentials_path: str | None = None) -> SheetsSync:
    """Return a SheetsSync instance using the default credentials path."""
    return SheetsSync(credentials_path)
