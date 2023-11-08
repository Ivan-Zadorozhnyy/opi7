import pytest
from main import app, setup_database

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        setup_database()

    yield client
