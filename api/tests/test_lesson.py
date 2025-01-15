
from uuid import uuid4
from datetime import date
from http import HTTPStatus

from api import models

def test_lesson_start(client, token, session, lesson):
    lesson.status = models.LessonStatus.WAITING
    lesson.effective_start_date = None
    session.commit()
    response = client.post(f"/logged/lesson/start/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.OK
    session.refresh(lesson)
    assert lesson.status == models.LessonStatus.RUNNING
    assert lesson.effective_start_date == date.today()

def test_start_undefined_lesson(client, token):
    response = client.post(f"/logged/lesson/start/{uuid4()}", auth=token)
    assert response.status_code == HTTPStatus.NOT_FOUND
    response = client.post("/logged/lesson/start/not-uuid", auth=token)
    assert response.status_code >= 400

def test_cannot_start_a_running_lesson(client, token, session, lesson):
    lesson.status = models.LessonStatus.RUNNING
    lesson.effective_start_date = date.today()
    session.commit()
    response = client.post(f"/logged/lesson/start/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.BAD_REQUEST
