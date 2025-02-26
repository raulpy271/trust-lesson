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


@pytest.fixture
def container():
    class ContainerMock:
        async def upload_blob(self, key, *args, **kwargs):
            self.key = key

    return ContainerMock()


def test_create(
    monkeypatch, session, client, token, image, lesson, user_password, container
):
    monkeypatch.setattr("api.azure.get_container_image", lambda: container)
    data = {
        "lesson_id": str(lesson.id),
    }
    resp = client.post(
        "logged/validation/create", auth=token, data=data, files={"file": image}
    )
    assert resp.status_code == HTTPStatus.CREATED
    validation = session.scalars(
        select(LessonValidation).where(
            (LessonValidation.lesson_id == lesson.id)
            & (LessonValidation.user_id == user_password[0].id)
        )
    ).one_or_none()
    assert validation
    assert container.key == validation.media_path


def test_create_invalid_lesson(client, token, image):
    data = {
        "lesson_id": str(uuid4()),
    }
    resp = client.post(
        "logged/validation/create", auth=token, data=data, files={"file": image}
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_create_invalid_media(client, token, lesson):
    data = {
        "lesson_id": str(lesson.id),
    }
    image = BytesIO(randbytes(100))
    resp = client.post(
        "logged/validation/create", auth=token, data=data, files={"file": image}
    )
    assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
