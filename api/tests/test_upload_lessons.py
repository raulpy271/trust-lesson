from http import HTTPStatus
from unittest.mock import MagicMock, AsyncMock

import pytest

from tests.factories import factory


@pytest.fixture
def lessons1():
    with open("tests/mock/lessons1.xlsx", "rb") as sp:
        yield sp


@pytest.fixture
def image():
    with open("tests/mock/validation.png", "rb") as img:
        yield img


def test_create(
    monkeypatch,
    session,
    client,
    token,
    lessons1,
    container,
    course,
    course_term,
    user_password,
):
    lessons = factory.list_lesson(10, session, course_term, user_password)
    mock = MagicMock()
    res = AsyncMock()
    res.json.return_value = {
        "course_id": str(course.id),
        "term_id": str(course_term.id),
    }
    mock.__aenter__.return_value = AsyncMock()
    mock.__aenter__.return_value.post.return_value = res

    monkeypatch.setattr("api.azure.get_container_spreadsheet", lambda: container)
    monkeypatch.setattr("api.lesson.function_session", lambda: mock)

    resp = client.post(
        "logged/lesson/upload-spreadsheet", auth=token, files={"file": lessons1}
    )
    course_resp = resp.json()
    assert resp.status_code == HTTPStatus.CREATED
    assert course_resp["id"] == str(course.id)
    assert len(course_resp["terms"]) == 1
    assert course_resp["terms"][0]["term_number"] == course_term.term_number
    assert len(course_resp["terms"][0]["lessons"]) == len(lessons)
    result_lessons = course_resp["terms"][0]["lessons"]
    for i, expected_lesson in enumerate(lessons):
        assert result_lessons[i]["id"] == str(expected_lesson.id)
        assert result_lessons[i]["title"] == expected_lesson.title
        assert result_lessons[i]["description"] == expected_lesson.description


def test_function_error(
    monkeypatch,
    client,
    token,
    lessons1,
    container,
):
    mock = MagicMock()
    res = AsyncMock()
    res.ok = False
    res.status = HTTPStatus.INTERNAL_SERVER_ERROR
    res.json.return_value = {
        "message": "function error",
        "errors": [],
        "state_error": None,
    }
    mock.__aenter__.return_value = AsyncMock()
    mock.__aenter__.return_value.post.return_value = res
    monkeypatch.setattr("api.azure.get_container_spreadsheet", lambda: container)
    monkeypatch.setattr("api.lesson.function_session", lambda: mock)
    resp = client.post(
        "logged/lesson/upload-spreadsheet", auth=token, files={"file": lessons1}
    )
    assert resp.status_code == res.status
    course_resp = resp.json()
    assert course_resp["detail"] == res.json.return_value


def test_create_wrong_media(client, token, image):
    resp = client.post(
        "logged/lesson/upload-spreadsheet", auth=token, files={"file": image}
    )
    assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
