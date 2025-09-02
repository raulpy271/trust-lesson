from datetime import datetime, timedelta

from api import models
from api.jobs.update_status_lesson import run


async def test_no_lesson_to_update(session, lesson):
    lesson.status = models.LessonStatus.WAITING
    lesson.start_date = datetime.now() + timedelta(days=2)
    await session.commit()
    await run()
    await session.refresh(lesson)
    assert lesson.status == models.LessonStatus.WAITING


async def test_update_one_waiting_lesson(session, lesson):
    lesson.status = models.LessonStatus.WAITING
    lesson.start_date = datetime.now() - timedelta(days=1, hours=1)
    await session.commit()
    await run()
    await session.refresh(lesson)
    assert lesson.status == models.LessonStatus.LATE
