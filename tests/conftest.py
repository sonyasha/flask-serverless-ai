import pytest

from api.app import app as flask_app


@pytest.fixture(scope="module")
def client():
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


@pytest.fixture
def sample_roadmap_data():
    return {"name": "Test User", "interests": ["frontend", "backend"], "timeframe": 6}
