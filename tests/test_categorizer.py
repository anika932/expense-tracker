from types import SimpleNamespace

from app.services.categorizer import categorize

CATEGORIES = [
    SimpleNamespace(name="Food", keywords="swiggy,zomato"),
    SimpleNamespace(name="Travel", keywords="uber"),
    SimpleNamespace(name="Other", keywords=""),
]


def test_matches_keyword():
    assert categorize("Swiggy order", CATEGORIES).name == "Food"


def test_is_case_insensitive():
    assert categorize("UBER RIDE", CATEGORIES).name == "Travel"


def test_falls_back_to_other():
    assert categorize("Rent to landlord", CATEGORIES).name == "Other"