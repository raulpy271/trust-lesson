
from dotenv import load_dotenv
load_dotenv("testing.env")

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.settings import DB_URL
from api.models import Base

@pytest.fixture
def session():
    engine = create_engine(DB_URL, echo=True)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s



