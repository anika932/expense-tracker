from decimal import Decimal

import pandas as pd

from app import db
from app.models import Category, Transaction
from app.services.categorizer import categorize

REQUIRED_COLUMNS = {"date", "description", "amount"}


class CsvError(Exception):
    """Raised when the uploaded CSV is invalid."""


def import_csv(file):
    """Import a CSV. Returns (saved, skipped_invalid, duplicates)."""
    # 1. Read the file
    try:
        df = pd.read_csv(file)
    except Exception:
        raise CsvError("Could not read the file. Please upload a valid CSV.")

    # 2. Validate columns
    df.columns = [c.strip().lower() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise CsvError("Missing columns: " + ", ".join(sorted(missing)))

    # 3. Clean data (bad values become NaT/NaN instead of crashing)
    total_rows = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["description"] = df["description"].fillna("").astype(str).str.strip()

    df = df.dropna(subset=["date", "amount"])
    df = df[df["description"] != ""]
    df = df[df["amount"] > 0]  # reject zero/negative amounts
    skipped = total_rows - len(df)

    if df.empty:
        raise CsvError("No valid rows found in the file.")

    # 4. Find transactions that already exist in the database
    dates = df["date"].dt.date.unique().tolist()
    existing = {
        (t.date, t.description, t.amount)
        for t in Transaction.query.filter(Transaction.date.in_(dates)).all()
    }

    # 5. Categorize and save only the new ones
    categories = Category.query.all()
    saved = 0
    duplicates = 0
    for row in df.itertuples():
        description = row.description[:255]
        amount = Decimal(str(round(row.amount, 2)))
        key = (row.date.date(), description, amount)

        if key in existing:
            duplicates += 1
            continue

        category = categorize(description, categories)
        db.session.add(
            Transaction(
                date=row.date.date(),
                description=description,
                amount=amount,
                category_id=category.id if category else None,
            )
        )
        saved += 1

    db.session.commit()
    return saved, skipped, duplicates