
from dotenv import load_dotenv
load_dotenv("testing.env")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import models, settings
from api import create_app

@pytest.fixture
def session():
    models._engine = create_engine(settings.DB_URL)
    models._session = sessionmaker(models._engine)
    models.Base.metadata.create_all(models._engine)
    with models.Session() as s:
        yield s

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

