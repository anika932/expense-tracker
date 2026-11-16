from datetime import date
from decimal import Decimal

from app import db
from app.models import Category, Transaction
from app.services.insights import find_unusual


def test_unusually_high_transaction_is_flagged(app):
    with app.app_context():
        food = Category.query.filter_by(name="Food").first()
        amounts = [100, 110, 90, 105, 95, 100, 102, 98, 5000]
        for i, amount in enumerate(amounts):
            db.session.add(
                Transaction(
                    date=date(2026, 11, i + 1),
                    description=f"Food item {i}",
                    amount=Decimal(amount),
                    category_id=food.id,
                )
            )
        db.session.commit()

        flagged = find_unusual(2026, 11)
        assert len(flagged) == 1
        assert flagged[0]["amount"] == 5000.0