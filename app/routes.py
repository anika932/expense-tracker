from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import text

from app import db
from app.models import Transaction
from app.services.csv_service import CsvError, import_csv

from flask import jsonify
from app.services import analytics

from decimal import Decimal, InvalidOperation
from app.models import Budget, Category, Transaction
from app.services import insights

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return redirect(url_for("main.upload"))


@bp.route("/db-check")
def db_check():
    db.session.execute(text("SELECT 1"))
    return "Database connected!"


@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("Please choose a file.", "error")
        elif not file.filename.lower().endswith(".csv"):
            flash("Only .csv files are allowed.", "error")
        else:
            try:
                saved, skipped, duplicates = import_csv(file)
                flash(
                    f"Imported {saved} new transactions. Skipped {skipped} invalid rows. "
                    f"Ignored {duplicates} duplicates.",
                    "success",
                )
            except CsvError as e:
                flash(str(e), "error")
        return redirect(url_for("main.upload"))

    transactions = Transaction.query.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(50).all()
    return render_template("upload.html", transactions=transactions)
@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@bp.route("/api/summary")
def api_summary():
    months = analytics.available_months()
    if not months:
        return jsonify({"months": [], "selected": None, "categories": [], "trend": []})

    selected = request.args.get("month")  # format: 2026-11
    try:
        year, month = (int(x) for x in selected.split("-"))
    except (AttributeError, ValueError):
        year, month = months[0]  # default: latest month

    return jsonify({
        "months": [f"{y}-{m:02d}" for y, m in months],
        "selected": f"{year}-{month:02d}",
        "categories": analytics.category_totals(year, month),
        "trend": analytics.monthly_totals(),
    })

def _parse_month(selected, months):
    try:
        year, month = (int(x) for x in selected.split("-"))
        return year, month
    except (AttributeError, ValueError):
        return months[0] if months else (None, None)


@bp.route("/api/insights")
def api_insights():
    months = analytics.available_months()
    year, month = _parse_month(request.args.get("month"), months)
    if not year:
        return jsonify({"budgets": [], "unusual": []})
    return jsonify({
        "budgets": insights.budget_status(year, month),
        "unusual": insights.find_unusual(year, month),
    })


@bp.route("/budgets", methods=["GET", "POST"])
def budgets():
    if request.method == "POST":
        category_id = request.form.get("category_id", type=int)
        try:
            limit = Decimal(request.form.get("monthly_limit", "").strip())
            if limit <= 0:
                raise InvalidOperation
        except InvalidOperation:
            flash("Enter a valid limit greater than 0.", "error")
            return redirect(url_for("main.budgets"))

        if not db.session.get(Category, category_id):
            flash("Invalid category.", "error")
            return redirect(url_for("main.budgets"))

        budget = Budget.query.filter_by(category_id=category_id).first()
        if budget:
            budget.monthly_limit = limit      # update existing
        else:
            db.session.add(Budget(category_id=category_id, monthly_limit=limit))
        db.session.commit()
        flash("Budget saved.", "success")
        return redirect(url_for("main.budgets"))

    return render_template(
        "budgets.html",
        categories=Category.query.order_by(Category.name).all(),
        budgets=Budget.query.all(),
    )

@bp.app_errorhandler(413)
def file_too_large(e):
    flash("File is too large. Maximum size is 5 MB.", "error")
    return redirect(url_for("main.upload"))