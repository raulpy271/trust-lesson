
from datetime import date, datetime
from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from sqlalchemy import select
from fastapi import APIRouter, HTTPException

from api import dto
from api.auth import LoggedUserId
from api.models import Session, Lesson, LessonUser, LessonStatus

router = APIRouter(
    prefix="/lesson",
    tags=["lesson"]
)

@router.get("/list")
def lesson_list(start_date: date, end_date: date, user_id: LoggedUserId):
    with Session() as session:
        stmt = (
            select(Lesson)
            .join(LessonUser)
            .where(
                (start_date <= Lesson.start_date) &
                (end_date >= Lesson.start_date) &
                (LessonUser.user_id == user_id)
            )
        )
        lessons = session.scalars(stmt).all()
    return {
        "lessons": [lesson.to_dict() for lesson in lessons]
    }

@router.post("/start/{lesson_id}")
def lesson_start(lesson_id: UUID, user_id: LoggedUserId):
    with Session() as session:
        lesson = session.get(Lesson, lesson_id)
        if lesson:
            if lesson.instructor_id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Only the instructor can start the lesson"
                )
            elif lesson.status.can_start():
                lesson.status = LessonStatus.RUNNING
                lesson.effective_start_date = datetime.now()
                session.commit()
            else:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="The selected lesson already started"
                )
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

@router.post("/stop/{lesson_id}")
def lesson_stop(lesson_id: UUID, user_id: LoggedUserId):
    with Session() as session:
        lesson = session.scalars(select(Lesson).where(Lesson.id == lesson_id)).one_or_none()
        if lesson:
            pass
            if lesson.instructor_id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Only the instructor can stop the lesson"
                )
            elif lesson.status.can_stop():
                lesson.status = LessonStatus.FINISHED
                duration = datetime.now() - lesson.effective_start_date
                lesson.effective_duration_min = int(duration.total_seconds() / 60)
                session.commit()
            else:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Cannot stop the current lesson."
                )
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

