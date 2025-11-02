from uuid import uuid4
from random import randbytes
from io import BytesIO
from http import HTTPStatus

import pytest
from sqlmodel import select

from api.models import LessonValidation


@pytest.fixture
def image():
    with open("tests/mock/validation.png", "rb") as img:
        yield img


@pytest.fixture
def spreadsheet():
    with open("tests/mock/lessons1.xlsx", "rb") as sp:
        yield sp


async def test_create(
    monkeypatch,
    session,
    client,
    token,
    image,
    lesson,
    user_password,
    lesson_user,
    container,
):
    monkeypatch.setattr(
        "api.routes.validation.lesson.get_container_image", lambda: container
    )
    data = {
        "lesson_id": str(lesson.id),
    }
    resp = client.post(
        "logged/lesson-validation", auth=token, data=data, files={"file": image}
    )
    validation_res = resp.json()
    assert resp.status_code == HTTPStatus.CREATED
    validation = (
        await session.exec(
            select(LessonValidation).where(
                LessonValidation.lesson_id == lesson.id,
                LessonValidation.user_id == user_password[0].id,
            )
        )
    ).first()
    assert validation
    assert str(validation.id) == validation_res["id"]
    assert container.key == validation.media_path


def test_create_invalid_lesson(client, token, image):
    data = {
        "lesson_id": str(uuid4()),
    }
    resp = client.post(
        "logged/lesson-validation", auth=token, data=data, files={"file": image}
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_create_invalid_media(client, token, lesson):
    data = {
        "lesson_id": str(lesson.id),
    }
    image = BytesIO(randbytes(100))
    resp = client.post(
        "logged/lesson-validation", auth=token, data=data, files={"file": image}
    )
    assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


def test_create_wrong_media(client, token, lesson, spreadsheet):
    data = {
        "lesson_id": str(lesson.id),
    }
    resp = client.post(
        "logged/lesson-validation", auth=token, data=data, files={"file": spreadsheet}
    )
    assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


async def test_list_identity_validation(
    client, session, factory, user_password, token, identity_validation
):
    new_user = await factory.user_password(session)
    await factory.identity_validation(session, new_user)
    resp = client.get("logged/identity-validation", auth=token)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert len(data) == 1
    validation_res = data[0]
    assert str(identity_validation.id) == validation_res["id"]
    assert str(user_password[0].id) == validation_res["user_id"]
    assert identity_validation.type.value == validation_res["type"]
    assert identity_validation.fullname == validation_res["fullname"]
    assert (
        identity_validation.fullname_confidence == validation_res["fullname_confidence"]
    )
    assert identity_validation.error_message == validation_res["error_message"]
    assert not validation_res.get("error_traceback")
