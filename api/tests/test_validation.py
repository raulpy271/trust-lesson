
from uuid import uuid4
from random import randbytes
from io import BytesIO
from http import HTTPStatus

import pytest
from sqlalchemy import select

from api import settings
from api.models import LessonValidation

@pytest.fixture
def image():
    with open("tests/mock/validation.png", "rb") as img:
        yield img

def test_create(client, token, image, lesson):
    data = {
        "lesson_id": str(lesson.id),
    }
    resp = client.post("logged/validation/create", auth=token, data=data, files={"file": image})
    assert resp.status_code == HTTPStatus.CREATED

def test_create_invalid_lesson(client, token, image, lesson):
    data = {
        "lesson_id": str(uuid4()),
    }
    resp = client.post("logged/validation/create", auth=token, data=data, files={"file": image})
    assert resp.status_code == HTTPStatus.NOT_FOUND

def test_create_invalid_media(client, token, lesson):
    data = {
        "lesson_id": str(lesson.id),
    }
    image = BytesIO(randbytes(100))
    resp = client.post("logged/validation/create", auth=token, data=data, files={"file": image})
    assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
