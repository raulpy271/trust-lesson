
from datetime import datetime, timedelta

from sqlalchemy import update

from api.models import Session, Lesson, LessonStatus

def run():
    with Session() as session:
        cut_date = datetime.now() - timedelta(days=1)
        stmt = (
            update(Lesson)
            .where(
                (Lesson.status == LessonStatus.WAITING) &
                (Lesson.start_date < cut_date)
            )
            .values(
                status=LessonStatus.LATE
            )
        )
        session.execute(stmt)
        session.commit()

