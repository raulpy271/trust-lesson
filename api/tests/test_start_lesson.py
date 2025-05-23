from uuid import uuid4
from datetime import datetime, timedelta
from http import HTTPStatus

from api import models
from tests.factories import factory
from tests.utils import authenticate


def test_lesson_start(client, token, session, lesson):
    lesson.status = models.LessonStatus.WAITING
    lesson.effective_start_date = None
    session.commit()
    response = client.post(f"/logged/lesson/start/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.OK
    session.refresh(lesson)
    assert lesson.status == models.LessonStatus.RUNNING
    assert isinstance(lesson.effective_start_date, datetime)
    assert (datetime.now() - lesson.effective_start_date) < timedelta(minutes=1)


def test_start_undefined_lesson(client, token):
    response = client.post(f"/logged/lesson/start/{uuid4()}", auth=token)
    assert response.status_code == HTTPStatus.NOT_FOUND
    response = client.post("/logged/lesson/start/not-uuid", auth=token)
    assert response.status_code >= 400


def test_cannot_start_a_running_lesson(client, token, session, lesson):
    lesson.status = models.LessonStatus.RUNNING
    lesson.effective_start_date = datetime.now()
    session.commit()
    response = client.post(f"/logged/lesson/start/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_only_instructor_can_start_lesson(client, session, lesson):
    u_password = factory.user_password(session)
    t = authenticate(client, u_password[0], u_password[1])
    assert lesson.instructor_id != u_password[0].id
    response = client.post(f"/logged/lesson/start/{lesson.id}", auth=t)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    lesson.instructor = u_password[0]
    session.commit()
    response = client.post(f"/logged/lesson/start/{lesson.id}", auth=t)
    assert response.status_code == HTTPStatus.OK
