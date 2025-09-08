from uuid import uuid4
from datetime import datetime, timedelta
from http import HTTPStatus

from api import models
from tests.utils import authenticate


async def test_lesson_stop(client, token, session, lesson):
    lesson.status = models.LessonStatus.RUNNING
    minutes = 30
    lesson.effective_start_date = datetime.now() - timedelta(minutes=minutes)
    lesson.effective_duration_min = 0
    await session.commit()
    response = client.post(f"/logged/lesson/stop/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.OK
    await session.refresh(lesson)
    assert lesson.status == models.LessonStatus.FINISHED
    assert lesson.effective_duration_min == minutes


async def test_stop_undefined_lesson(client, token):
    response = client.post(f"/logged/lesson/stop/{uuid4()}", auth=token)
    assert response.status_code == HTTPStatus.NOT_FOUND
    response = client.post("/logged/lesson/stop/not-uuid", auth=token)
    assert response.status_code >= 400


async def test_cannot_stop_already_stopped_lesson(client, token, session, lesson):
    lesson.status = models.LessonStatus.FINISHED
    await session.commit()
    response = client.post(f"/logged/lesson/stop/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.BAD_REQUEST


async def test_only_instructor_can_stop_lesson(client, session, lesson, factory):
    lesson.status = models.LessonStatus.RUNNING
    lesson.effective_start_date = datetime.now()
    await session.commit()
    u_password = await factory.user_password(session)
    t = authenticate(client, u_password[0], u_password[1])
    assert lesson.instructor_id != u_password[0].id
    response = client.post(f"/logged/lesson/stop/{lesson.id}", auth=t)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    lesson.instructor = u_password[0]
    await session.commit()
    response = client.post(f"/logged/lesson/stop/{lesson.id}", auth=t)
    assert response.status_code == HTTPStatus.OK
