from sqlalchemy import extract, func

from app import db
from app.models import Category, Transaction


def available_months():
    """Return list of (year, month) that have transactions, newest first."""
    rows = (
        db.session.query(
            extract("year", Transaction.date).label("y"),
            extract("month", Transaction.date).label("m"),
        )
        .group_by("y", "m")
        .order_by(db.text("y DESC"), db.text("m DESC"))
        .all()
    )
    return [(int(r.y), int(r.m)) for r in rows]


def category_totals(year, month):
    """Total spending per category for one month."""
    rows = (
        db.session.query(
            func.coalesce(Category.name, "Uncategorized"),
            func.sum(Transaction.amount),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(extract("year", Transaction.date) == year)
        .filter(extract("month", Transaction.date) == month)
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    return [{"category": name, "total": float(total)} for name, total in rows]


def monthly_totals():
    """Total spending for every month (for the trend chart)."""
    rows = (
        db.session.query(
            extract("year", Transaction.date).label("y"),
            extract("month", Transaction.date).label("m"),
            func.sum(Transaction.amount),
        )
        .group_by("y", "m")
        .order_by(db.text("y"), db.text("m"))
        .all()
    )
    return [{"month": f"{int(y)}-{int(m):02d}", "total": float(t)} for y, m, t in rows]