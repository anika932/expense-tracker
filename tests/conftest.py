import pytest

from app import create_app, db


class ConfigForTests:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret"


@pytest.fixture
def app():
    app = create_app(ConfigForTests)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()