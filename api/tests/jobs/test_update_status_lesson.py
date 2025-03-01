from datetime import datetime, timedelta

from api import models
from api.jobs.update_status_lesson import run


def test_no_lesson_to_update(session, lesson):
    lesson.status = models.LessonStatus.WAITING
    lesson.effective_start_date = None
    session.commit()
    run()
    lesson = session.get(models.Lesson, lesson.id)
    assert lesson.status == models.LessonStatus.WAITING


def test_update_one_waiting_lesson(session, lesson):
    lesson.status = models.LessonStatus.WAITING
    lesson.start_date = datetime.now() - timedelta(days=1, hours=1)
    lesson.effective_start_date = None
    session.commit()
    run()
    lesson = session.get(models.Lesson, lesson.id)
    assert lesson.status == models.LessonStatus.LATE
