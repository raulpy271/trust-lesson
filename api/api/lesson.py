from datetime import date, datetime
from typing import Annotated
from uuid import UUID
from http import HTTPStatus

import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from api.dto import CreateLessonIn, UpdateLessonIn, UploadSpreadsheetLessons
from api.utils import function_session
from fastapi import APIRouter, HTTPException, Form
from azure.storage.blob import ContentSettings

from api.auth import LoggedUserId
from api.crud import crud_router
from api import azure
from api.models import (
    Session,
    Lesson,
    User,
    CourseTerm,
    Course,
    UserRole,
    LessonUser,
    LessonStatus,
)


def auth(_: None | CreateLessonIn, user: User, _resource_id: None | UUID):
    return user.is_admin or user.role in [UserRole.INSTRUCTOR, UserRole.ADMIN]


router = APIRouter(prefix="/lesson", tags=["lesson"])


@router.get("/list")
def lesson_list(start_date: date, end_date: date, user_id: LoggedUserId):
    date_filter = (start_date <= Lesson.start_date) & (end_date >= Lesson.start_date)
    with Session() as session:
        role = session.scalars(select(User.role).filter_by(id=user_id)).one()
        if role == UserRole.STUDANT:
            stmt = (
                select(Lesson)
                .join(LessonUser)
                .where(date_filter & (LessonUser.user_id == user_id))
            )
        else:
            stmt = select(Lesson).where(date_filter & (Lesson.instructor_id == user_id))
        lessons = session.scalars(stmt).all()
    return {"lessons": [lesson.to_dict() for lesson in lessons]}


@router.post("/start/{lesson_id}")
def lesson_start(lesson_id: UUID, user_id: LoggedUserId):
    with Session() as session:
        lesson = session.get(Lesson, lesson_id)
        if lesson:
            if lesson.instructor_id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Only the instructor can start the lesson",
                )
            elif lesson.status.can_start():
                lesson.status = LessonStatus.RUNNING
                lesson.effective_start_date = datetime.now()
                session.commit()
            else:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="The selected lesson already started",
                )
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("/stop/{lesson_id}")
def lesson_stop(lesson_id: UUID, user_id: LoggedUserId):
    with Session() as session:
        lesson = session.scalars(
            select(Lesson).where(Lesson.id == lesson_id)
        ).one_or_none()
        if lesson:
            pass
            if lesson.instructor_id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Only the instructor can stop the lesson",
                )
            elif lesson.status.can_stop():
                lesson.status = LessonStatus.FINISHED
                duration = datetime.now() - lesson.effective_start_date
                lesson.effective_duration_min = int(duration.total_seconds() / 60)
                session.commit()
            else:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Cannot stop the current lesson.",
                )
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("/upload-spreadsheet", status_code=HTTPStatus.CREATED)
async def upload_spreadsheet(data: Annotated[UploadSpreadsheetLessons, Form()]):
    try:
        container = azure.get_container_spreadsheet()
        await container.upload_blob(
            data.file.filename,
            data.file,
            content_settings=ContentSettings(content_type=data.file.content_type),
        )
        session = function_session()
        async with session as client:
            res = await client.post(
                "/api/lesson/upload-spreadsheet", data={"filename": data.file.filename}
            )
            res_json = await res.json()
        if res.ok:
            if res_json.get("course_id") and res_json.get("term_id"):
                with Session() as session:
                    course = session.get(Course, UUID(res_json["course_id"]))
                    term = session.scalars(
                        select(CourseTerm)
                        .options(selectinload(CourseTerm.lessons))
                        .where(CourseTerm.id == UUID(res_json["term_id"]))
                    ).first()
                if course and term:
                    course_dict = course.to_dict()
                    course_dict["terms"] = [term.to_dict()]
                    return course_dict
                else:
                    logging.error("The term lesson was not created")
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                logging.error(
                    "The keys 'course_id' and 'term_id' was not set on function response"  # noqa: E501
                )
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            logging.error("function error: " + res_json["error"])
            raise HTTPException(
                status_code=res.status,
                detail=res_json["error"],
            )
    except Exception as e:
        logging.error(str(e))
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


crud_router(
    Lesson,
    {"create": CreateLessonIn, "update": UpdateLessonIn, "delete": dict},
    authorizations={"default": auth, "get": None},
    methods=["get", "create", "put", "delete"],
    router=router,
)
