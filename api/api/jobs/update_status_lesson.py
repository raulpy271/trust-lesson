from datetime import datetime, timedelta

from sqlmodel import update

from api.models import AsyncSession, Lesson, LessonStatus


async def run():
    async with AsyncSession() as session:
        cut_date = datetime.now() - timedelta(days=1)
        stmt = (
            update(Lesson)
            .where(Lesson.status == LessonStatus.WAITING, Lesson.start_date < cut_date)
            .values(status=LessonStatus.LATE)
        )
        await session.exec(stmt)
        await session.commit()
