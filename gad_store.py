from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any


def _norm(s: str) -> str:
    return "".join(ch.lower() for ch in s.strip() if ch.isalnum())


def _safe_float(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


BudgetRow = dict[str, Any]


class BudgetStore:
    def list_items(self, *, filters: dict[str, str]) -> list[BudgetRow]:
        raise NotImplementedError

    def distinct(self) -> dict[str, list[str]]:
        raise NotImplementedError

    def get_item(self, item_id: int) -> BudgetRow | None:
        raise NotImplementedError

    def add_item(self, row: BudgetRow) -> None:
        raise NotImplementedError

    def update_item(self, item_id: int, row: BudgetRow) -> None:
        raise NotImplementedError

    def delete_item(self, item_id: int) -> None:
        raise NotImplementedError

    def dashboard(self) -> dict[str, Any]:
        raise NotImplementedError

    # --- NEW ---
    def get_summary(self) -> dict[str, Any]:
        raise NotImplementedError

    def list_expenditures(self) -> list[BudgetRow]:
        raise NotImplementedError

    def list_aip_programs(self) -> list[BudgetRow]:
        raise NotImplementedError


class SQLiteStore(BudgetStore):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    def _ensure_db(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS budgets (
                  id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                  no                      TEXT,
                  date                    TEXT,
                  office                  TEXT NOT NULL DEFAULT '',
                  status                  TEXT NOT NULL DEFAULT 'Planned',
                  particulars             TEXT,
                  pow_title               TEXT,
                  pow_date_of_activity    TEXT,
                  reference_code          TEXT,
                  ppa_allotted_budget     REAL NOT NULL DEFAULT 0,
                  ppa_description         TEXT,
                  accounts                TEXT,
                  account_code            TEXT,
                  proposed_budget         REAL NOT NULL DEFAULT 0,
                  actual_obligation       REAL NOT NULL DEFAULT 0,
                  payee                   TEXT,
                  caf                     TEXT,
                  obligation_number       TEXT,
                  venue_food_honorarium   TEXT,
                  actual_remaining_budget REAL NOT NULL DEFAULT 0,
                  remarks                 TEXT,
                  created_at              TEXT NOT NULL
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS office_summary (
                  id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                  office                TEXT NOT NULL,
                  budget_threshold      REAL NOT NULL DEFAULT 0,
                  obligated             REAL NOT NULL DEFAULT 0,
                  earnmarked            REAL NOT NULL DEFAULT 0,
                  expenses              REAL NOT NULL DEFAULT 0,
                  balance               REAL NOT NULL DEFAULT 0,
                  utilization_pct       REAL NOT NULL DEFAULT 0
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS expenditures (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  no              TEXT,
                  object_name     TEXT NOT NULL,
                  account_code    TEXT,
                  allotted_budget REAL NOT NULL DEFAULT 0,
                  earnmarked      REAL NOT NULL DEFAULT 0,
                  actual_obligated REAL NOT NULL DEFAULT 0,
                  expenses_total  REAL NOT NULL DEFAULT 0,
                  balance_budget  REAL NOT NULL DEFAULT 0
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS aip_programs (
                  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                  ref_code           TEXT,
                  office             TEXT,
                  description        TEXT NOT NULL,
                  ps_budget          REAL NOT NULL DEFAULT 0,
                  mooe_budget        REAL NOT NULL DEFAULT 0,
                  co_budget          REAL NOT NULL DEFAULT 0,
                  total_budget       REAL NOT NULL DEFAULT 0,
                  earnmarked         REAL NOT NULL DEFAULT 0,
                  obligated          REAL NOT NULL DEFAULT 0,
                  expenses           REAL NOT NULL DEFAULT 0,
                  balance            REAL NOT NULL DEFAULT 0,
                  status             TEXT,
                  utilization_pct    REAL NOT NULL DEFAULT 0,
                  quarterly_schedule TEXT,
                  is_header          INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS grand_totals (
                  id                       INTEGER PRIMARY KEY AUTOINCREMENT,
                  total_gad_threshold      REAL NOT NULL DEFAULT 0,
                  total_obligated          REAL NOT NULL DEFAULT 0,
                  total_earnmarked         REAL NOT NULL DEFAULT 0,
                  total_expenses           REAL NOT NULL DEFAULT 0,
                  utilization_pct          REAL NOT NULL DEFAULT 0,
                  ps_expenses              REAL NOT NULL DEFAULT 0,
                  ps_balance               REAL NOT NULL DEFAULT 0,
                  mooe_expenses            REAL NOT NULL DEFAULT 0,
                  mooe_balance             REAL NOT NULL DEFAULT 0,
                  co_expenses              REAL NOT NULL DEFAULT 0,
                  co_balance               REAL NOT NULL DEFAULT 0
                )
                """
            )

            db.commit()

            # Only seed budgets if empty (other tables seeded via migrate)
            cur = db.execute("SELECT COUNT(*) AS c FROM budgets")
            count = cur.fetchone()["c"]
            if count:
                return

            now = _iso_now()
            seed = [
                (
                    "1", "1/7/2026", "MGADO", "Completed",
                    "SALARY & INCENTIVES", None, None,
                    "1000-001-3-9-99-001-001-001-001", 7769794.00,
                    "Provision of Permanent",
                    "PS-Salaries & Wages-Regular", "5-01-01-010",
                    0.00, 87592.00, "PHILIPPINE VETERANS BANK", None, "101-26-01-015",
                    "SALARY", 6899501.24, None, now,
                ),
                (
                    "2", "1/7/2026", "MGADO", "Completed",
                    "SALARY & INCENTIVES", None, None,
                    "1000-001-3-9-99-001-001-001-001", 7769794.00,
                    "Provision of Permanent",
                    "PS-Personal Economic Relief Allowance (PERA)", "5-01-02-010",
                    0.00, 10000.00, "PHILIPPINE VETERANS BANK", None, "101-26-01-015",
                    "SALARY", 6899501.24, None, now,
                ),
                (
                    "3", "1/7/2026", "MGADO", "Completed",
                    "SALARY & INCENTIVES", None, None,
                    "1000-001-3-9-99-001-001-001-001", 7769794.00,
                    "Provision of Permanent",
                    "PS-Retirement and Life Insurance Premiums", "5-01-03-010",
                    0.00, 21022.08, "PHILIPPINE VETERANS BANK", None, "101-26-01-015",
                    "SALARY", 6899501.24, None, now,
                ),
                (
                    "6", "1/15/2026", "MSWDO", "Completed",
                    "INCENTIVES FOR THE CHILD DEVELOPMENT WORKERS (CDWs)",
                    "INCENTIVES FOR THE CHILD DEVELOPMENT WORKERS (CDWs)", "JANUARY",
                    "1000-001-3-9-99-001-003-013-001", 7200000.00,
                    "Provision of Honoraria for 90 Child Development Center Workers",
                    "MOOE-Other Maintenance and Operating Expenses", "5-02-99-990",
                    4675000.00, 425000.00, "JENIFER EVANGELISTA", None, "101-26-01-75",
                    "Honorarium", 1675000.00, None, now,
                ),
                (
                    "7", "1/21/2026", "MGADO", "Completed",
                    "CASH ADVANCE",
                    "BARANGAY GAD FOCAL POINT SYSTEM (BGFPS) 1ST MONTHLY MEETING FOR THE YEAR 2026",
                    "January 23, 2026",
                    "1000-001-3-9-99-001-002-002-001", 300000.00,
                    "Barangay GAD Focals",
                    "MOOE-Other Maintenance and Operating Expenses", "5-02-99-990",
                    0.00, 24000.00, "REYNAN PARADERO", None, "101-26-01-109",
                    "Cash Advance", 246750.00, None, now,
                ),
            ]
            db.executemany(
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
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                seed,
            )
            db.commit()

    # ─────────────────────────────────────
    # MONITORING (budgets) — existing
    # ─────────────────────────────────────

    def list_items(self, *, filters: dict[str, str]) -> list[BudgetRow]:
        office = (filters.get("office") or "").strip()
        status = (filters.get("status") or "").strip()
        q = (filters.get("q") or "").strip()

        where = []
        params: list[object] = []
        if office:
            where.append("office = ?")
            params.append(office)
        if status:
            where.append("status = ?")
            params.append(status)
        if q:
            where.append(
                "(particulars LIKE ? OR pow_title LIKE ? OR office LIKE ? OR payee LIKE ? OR ppa_description LIKE ?)"
            )
            params.extend([f"%{q}%"] * 5)

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        with self._connect() as db:
            cur = db.execute(
                f"""
                SELECT
                  id, no, date, office, status, particulars,
                  pow_title, pow_date_of_activity, reference_code,
                  ppa_allotted_budget, ppa_description,
                  accounts, account_code,
                  proposed_budget, actual_obligation,
                  payee, caf, obligation_number,
                  venue_food_honorarium, actual_remaining_budget,
                  remarks, created_at
                FROM budgets
                {where_sql}
                ORDER BY id ASC
                """,
                params,
            )
            return [dict(r) for r in cur.fetchall()]

    def distinct(self) -> dict[str, list[str]]:
        with self._connect() as db:
            offices = [r["office"] for r in db.execute(
                "SELECT DISTINCT office FROM budgets WHERE office != '' ORDER BY office ASC"
            ).fetchall()]
            statuses = [r["status"] for r in db.execute(
                "SELECT DISTINCT status FROM budgets ORDER BY status ASC"
            ).fetchall()]
        return {"office": offices, "status": statuses}

    def get_item(self, item_id: int) -> BudgetRow | None:
        with self._connect() as db:
            cur = db.execute("SELECT * FROM budgets WHERE id = ?", [item_id])
            r = cur.fetchone()
            return dict(r) if r else None

    def add_item(self, row: BudgetRow) -> None:
        with self._connect() as db:
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
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                [
                    row.get("no"), row.get("date"), row.get("office", ""),
                    row.get("status", "Planned"), row.get("particulars"),
                    row.get("pow_title"), row.get("pow_date_of_activity"),
                    row.get("reference_code"),
                    _safe_float(row.get("ppa_allotted_budget")),
                    row.get("ppa_description"),
                    row.get("accounts"), row.get("account_code"),
                    _safe_float(row.get("proposed_budget")),
                    _safe_float(row.get("actual_obligation")),
                    row.get("payee"), row.get("caf"),
                    row.get("obligation_number"),
                    row.get("venue_food_honorarium"),
                    _safe_float(row.get("actual_remaining_budget")),
                    row.get("remarks"),
                    _iso_now(),
                ],
            )
            db.commit()

    def update_item(self, item_id: int, row: BudgetRow) -> None:
        with self._connect() as db:
            db.execute(
                """
                UPDATE budgets
                SET no=?, date=?, office=?, status=?, particulars=?,
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
                    row.get("no"), row.get("date"), row.get("office", ""),
                    row.get("status", "Planned"), row.get("particulars"),
                    row.get("pow_title"), row.get("pow_date_of_activity"),
                    row.get("reference_code"),
                    _safe_float(row.get("ppa_allotted_budget")),
                    row.get("ppa_description"),
                    row.get("accounts"), row.get("account_code"),
                    _safe_float(row.get("proposed_budget")),
                    _safe_float(row.get("actual_obligation")),
                    row.get("payee"), row.get("caf"),
                    row.get("obligation_number"),
                    row.get("venue_food_honorarium"),
                    _safe_float(row.get("actual_remaining_budget")),
                    row.get("remarks"),
                    item_id,
                ],
            )
            db.commit()

    def delete_item(self, item_id: int) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM budgets WHERE id = ?", [item_id])
            db.commit()

    def dashboard(self) -> dict[str, Any]:
        with self._connect() as db:
            totals = db.execute(
                """
                SELECT
                  COUNT(*) AS items,
                  COALESCE(SUM(ppa_allotted_budget), 0) AS allocated,
                  COALESCE(SUM(actual_obligation), 0) AS obligated,
                  COALESCE(SUM(actual_remaining_budget), 0) AS disbursed
                FROM budgets
                """
            ).fetchone()

            by_category = db.execute(
                """
                SELECT
                  office AS category,
                  COUNT(*) AS items,
                  COALESCE(SUM(ppa_allotted_budget), 0) AS allocated,
                  COALESCE(SUM(actual_obligation), 0) AS obligated,
                  COALESCE(SUM(actual_remaining_budget), 0) AS disbursed
                FROM budgets
                GROUP BY office
                ORDER BY allocated DESC
                """
            ).fetchall()

            recent = db.execute(
                """
                SELECT id, no, date, office, particulars, ppa_allotted_budget,
                       actual_obligation, actual_remaining_budget, status, created_at
                FROM budgets
                ORDER BY id DESC
                LIMIT 8
                """
            ).fetchall()

        return {
            "totals": dict(totals),
            "by_category": [dict(r) for r in by_category],
            "recent": [dict(r) for r in recent],
        }

    # ─────────────────────────────────────
    # SUMMARY — office-level + grand totals
    # ─────────────────────────────────────

    def get_summary(self) -> dict[str, Any]:
        with self._connect() as db:
            # grand totals
            gt_row = db.execute("SELECT * FROM grand_totals LIMIT 1").fetchone()
            grand = dict(gt_row) if gt_row else {
                "total_gad_threshold": 0, "total_obligated": 0,
                "total_earnmarked": 0, "total_expenses": 0,
                "utilization_pct": 0,
                "ps_expenses": 0, "ps_balance": 0,
                "mooe_expenses": 0, "mooe_balance": 0,
                "co_expenses": 0, "co_balance": 0,
            }

            # per-office
            offices = db.execute(
                """
                SELECT * FROM office_summary
                ORDER BY budget_threshold DESC
                """
            ).fetchall()

        return {
            "grand": grand,
            "offices": [dict(r) for r in offices],
        }

    # ─────────────────────────────────────
    # EXPENDITURES (LBP2-Accounts)
    # ─────────────────────────────────────

    def list_expenditures(self) -> list[BudgetRow]:
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT * FROM expenditures
                ORDER BY id ASC
                """
            ).fetchall()
        return [dict(r) for r in rows]

    # ─────────────────────────────────────
    # AIP PROGRAMS (LBP4-AIP-Obligated)
    # ─────────────────────────────────────

    def list_aip_programs(self) -> list[BudgetRow]:
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT * FROM aip_programs
                ORDER BY id ASC
                """
            ).fetchall()
        return [dict(r) for r in rows]


def make_store(sqlite_db_path: str) -> BudgetStore:
    return SQLiteStore(sqlite_db_path)
