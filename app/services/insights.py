from statistics import mean, pstdev

from sqlalchemy import extract, func

from app import db
from app.models import Budget, Category, Transaction


def budget_status(year, month):
    """Compare this month's spending with each category's monthly limit."""
    result = []
    for budget in Budget.query.all():
        spent = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(Transaction.category_id == budget.category_id)
            .filter(extract("year", Transaction.date) == year)
            .filter(extract("month", Transaction.date) == month)
            .scalar()
        )
        spent = float(spent)
        limit = float(budget.monthly_limit)
        percent = round(spent / limit * 100, 1) if limit else 0

        if percent >= 100:
            level = "danger"
        elif percent >= 80:
            level = "warning"
        else:
            level = "ok"

        result.append({
            "category": budget.category.name,
            "spent": spent,
            "limit": limit,
            "percent": percent,
            "level": level,
        })
    return result


def find_unusual(year, month, threshold=2.0, min_history=3):
    """Flag transactions far above their category's normal amount (Z-score)."""
    flagged = []

    for category in Category.query.all():
        amounts = [
            float(t.amount)
            for t in Transaction.query.filter_by(category_id=category.id).all()
        ]
        if len(amounts) < min_history:
            continue  # not enough history to say what is "normal"

        avg = mean(amounts)
        std = pstdev(amounts)
        if std == 0:
            continue

        month_txns = (
            Transaction.query.filter_by(category_id=category.id)
            .filter(extract("year", Transaction.date) == year)
            .filter(extract("month", Transaction.date) == month)
            .all()
        )
        for t in month_txns:
            z = (float(t.amount) - avg) / std
            if z >= threshold:
                flagged.append({
                    "date": t.date.isoformat(),
                    "description": t.description,
                    "amount": float(t.amount),
                    "category": category.name,
                    "average": round(avg, 2),
                    "z_score": round(z, 2),
                })

    return sorted(flagged, key=lambda x: x["z_score"], reverse=True)