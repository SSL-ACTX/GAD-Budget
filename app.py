import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from gad_store import BudgetStore, make_store
from sync_spreadsheet import SpreadsheetSync


APP_NAME = "GAD Budget Monitoring"
DB_FILENAME = "gad_budget.db"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    app.config["DATABASE"] = os.path.join(app.root_path, DB_FILENAME)

    store = make_store(app.config["DATABASE"])
    app.extensions["budget_store"] = store

    @app.get("/")
    def welcome():
        return render_template("welcome.html", app_name=APP_NAME)

    @app.get("/dashboard")
    def dashboard():
        s = get_store(app)
        data = s.dashboard()
        rows = data["by_category"]
        totals = data["totals"]
        recent = data["recent"]

        # Get summary data for the dashboard cards
        summary = s.get_summary()

        return render_template(
            "dashboard.html",
            app_name=APP_NAME,
            rows=rows,
            totals=totals,
            recent=recent,
            summary=summary,
        )

    @app.get("/tables")
    def tables():
        s = get_store(app)
        filters = {
            "office": (request.args.get("office") or "").strip(),
            "status": (request.args.get("status") or "").strip(),
            "q": (request.args.get("q") or "").strip(),
        }
        items = s.list_items(filters=filters)
        distinct = s.distinct()

        return render_template(
            "tables.html",
            app_name=APP_NAME,
            items=items,
            distinct=distinct,
            filters=filters,
        )

    @app.post("/tables/add")
    def add_budget():
        data = parse_budget_form(request.form)
        if not data["ok"]:
            flash(data["error"], "danger")
            return redirect(url_for("tables"))

        s = get_store(app)
        s.add_item(data)

        flash("Record added successfully.", "success")
        return redirect(url_for("tables"))

    @app.get("/tables/<int:item_id>/edit")
    def edit_budget(item_id: int):
        s = get_store(app)
        row = s.get_item(item_id)
        if row is None:
            flash("Item not found.", "warning")
            return redirect(url_for("tables"))
        return render_template("edit.html", app_name=APP_NAME, item=row)

    @app.post("/tables/<int:item_id>/edit")
    def edit_budget_post(item_id: int):
        s = get_store(app)
        existing = s.get_item(item_id)
        if existing is None:
            flash("Item not found.", "warning")
            return redirect(url_for("tables"))

        data = parse_budget_form(request.form)
        if not data["ok"]:
            flash(data["error"], "danger")
            return redirect(url_for("edit_budget", item_id=item_id))

        s.update_item(item_id, data)

        flash("Record updated successfully.", "success")
        return redirect(url_for("tables"))

    @app.post("/tables/<int:item_id>/delete")
    def delete_budget(item_id: int):
        s = get_store(app)
        s.delete_item(item_id)
        flash("Record deleted.", "success")
        return redirect(url_for("tables"))

    @app.post("/sync")
    def sync_data():
        excel_path = os.path.join(app.root_path, "GAD BUDGET MONITORING 2026.xlsx")
        # In a real app, you might want to fetch from a URL if configured
        sync = SpreadsheetSync(app.config["DATABASE"], excel_path=excel_path)
        ok, msg = sync.sync()
        if ok:
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("tables"))

    # ──────────────────────────────────
    # NEW: Summary page
    # ──────────────────────────────────
    @app.get("/summary")
    def summary():
        s = get_store(app)
        data = s.get_summary()
        return render_template(
            "summary.html",
            app_name=APP_NAME,
            grand=data["grand"],
            offices=data["offices"],
        )

    # ──────────────────────────────────
    # NEW: Expenditures page (LBP2)
    # ──────────────────────────────────
    @app.get("/expenditures")
    def expenditures():
        s = get_store(app)
        items = s.list_expenditures()
        return render_template(
            "expenditures.html",
            app_name=APP_NAME,
            items=items,
        )

    # ──────────────────────────────────
    # NEW: AIP Programs page (LBP4)
    # ──────────────────────────────────
    @app.get("/aip-programs")
    def aip_programs():
        s = get_store(app)
        items = s.list_aip_programs()
        return render_template(
            "aip_programs.html",
            app_name=APP_NAME,
            items=items,
        )

    @app.get("/api/dashboard/summary")
    def api_dashboard_summary():
        s = get_store(app)
        data = s.dashboard()
        totals = data["totals"]
        by_category = [
            {"category": r["category"], "allocated": r["allocated"], "disbursed": r["disbursed"]}
            for r in data["by_category"]
        ]
        return jsonify({"totals": totals, "by_category": by_category})

    return app


def get_store(app: Flask) -> BudgetStore:
    return app.extensions["budget_store"]


def parse_budget_form(form) -> dict:
    office = (form.get("office") or "").strip()
    status = (form.get("status") or "").strip() or "Planned"

    if not office:
        return {"ok": False, "error": "Office is required."}

    try:
        ppa_allotted_budget = to_money(form.get("ppa_allotted_budget"))
        proposed_budget = to_money(form.get("proposed_budget"))
        actual_obligation = to_money(form.get("actual_obligation"))
        actual_remaining_budget = to_money(form.get("actual_remaining_budget"))
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    return {
        "ok": True,
        "no": (form.get("no") or "").strip(),
        "date": (form.get("date") or "").strip(),
        "office": office,
        "status": status,
        "particulars": (form.get("particulars") or "").strip(),
        "pow_title": (form.get("pow_title") or "").strip(),
        "pow_date_of_activity": (form.get("pow_date_of_activity") or "").strip(),
        "reference_code": (form.get("reference_code") or "").strip(),
        "ppa_allotted_budget": float(ppa_allotted_budget),
        "ppa_description": (form.get("ppa_description") or "").strip(),
        "accounts": (form.get("accounts") or "").strip(),
        "account_code": (form.get("account_code") or "").strip(),
        "proposed_budget": float(proposed_budget),
        "actual_obligation": float(actual_obligation),
        "payee": (form.get("payee") or "").strip(),
        "caf": (form.get("caf") or "").strip(),
        "obligation_number": (form.get("obligation_number") or "").strip(),
        "venue_food_honorarium": (form.get("venue_food_honorarium") or "").strip(),
        "actual_remaining_budget": float(actual_remaining_budget),
        "remarks": (form.get("remarks") or "").strip(),
    }


def to_money(val) -> Decimal:
    s = (val or "").strip()
    if not s:
        return Decimal("0")
    s = s.replace(",", "")
    try:
        d = Decimal(s)
    except InvalidOperation:
        raise ValueError("Amounts must be numeric (example: 120000 or 120000.50).")
    return d.quantize(Decimal("0.01"))


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
