import io

import pytest

from app.models import Transaction
from app.services.csv_service import CsvError, import_csv


def make_csv(text):
    return io.BytesIO(text.encode("utf-8"))


GOOD = "date,description,amount\n2026-11-01,Swiggy order,349.50\n2026-11-02,Uber ride,220\n"


def test_import_valid_file(app):
    with app.app_context():
        assert import_csv(make_csv(GOOD)) == (2, 0, 0)
        assert Transaction.query.count() == 2


def test_invalid_rows_are_skipped(app):
    bad = GOOD + "not-a-date,Broken row,abc\n"
    with app.app_context():
        assert import_csv(make_csv(bad)) == (2, 1, 0)


def test_negative_amount_is_skipped(app):
    data = GOOD + "2026-11-03,Refund,-50\n"
    with app.app_context():
        assert import_csv(make_csv(data)) == (2, 1, 0)


def test_duplicate_upload_is_ignored(app):
    with app.app_context():
        import_csv(make_csv(GOOD))
        assert import_csv(make_csv(GOOD)) == (0, 0, 2)
        assert Transaction.query.count() == 2


def test_missing_column_raises_error(app):
    with app.app_context():
        with pytest.raises(CsvError):
            import_csv(make_csv("date,amount\n2026-11-01,100\n"))