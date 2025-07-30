import pytest
from app import create_app
from database import db as _db

@pytest.fixture(scope='function')
def app():
    # crea app con modo testing, que usa sqlite en memoria
    app = create_app(testing=True)

    # contexto app necesario para operaciones con db
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        yield _db.session
