from datetime import date, datetime
from typing import Annotated
from uuid import UUID
from http import HTTPStatus

import logging
from sqlmodel import select
from sqlalchemy.orm import selectinload
from api.dto import CreateLessonIn, UpdateLessonIn, UploadSpreadsheetLessons
from api.azure.functions import function_session
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from azure.storage.blob import ContentSettings

from api.depends import LoggedUserId, SessionDep
from api.crud import crud_router
from api.azure.storage import get_container_spreadsheet
from api.models import (
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


@router.get(
    "/list",
    response_model=list[Lesson.response_model({"term", "instructor"})],
)
def lesson_list(
    start_date: date, end_date: date, user_id: LoggedUserId, session: SessionDep
):
    date_filter = (start_date <= Lesson.start_date) & (end_date >= Lesson.start_date)
    role = session.exec(select(User.role).filter_by(id=user_id)).one()
    if role == UserRole.STUDANT:
        stmt = (
            select(Lesson)
            .join(LessonUser)
            .where(date_filter & (LessonUser.user_id == user_id))
        )
    else:
        stmt = select(Lesson).where(date_filter & (Lesson.instructor_id == user_id))
    lessons = session.exec(stmt).all()
    return lessons


@router.post("/start/{lesson_id}", response_model=Lesson.response_model())
def lesson_start(lesson_id: UUID, user_id: LoggedUserId, session: SessionDep):
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
            return lesson
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="The selected lesson already started",
            )
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("/stop/{lesson_id}", response_model=Lesson.response_model())
def lesson_stop(lesson_id: UUID, user_id: LoggedUserId, session: SessionDep):
    lesson = session.get(Lesson, lesson_id)
    if lesson:
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
            return lesson
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Cannot stop the current lesson.",
            )
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post(
    "/upload-spreadsheet",
    status_code=HTTPStatus.CREATED,
    response_model=CourseTerm.response_model({"course", "lessons"}),
)
async def upload_spreadsheet(
    data: Annotated[UploadSpreadsheetLessons, Form()],
    user_id: LoggedUserId,
    session: SessionDep,
):
    try:
        container = get_container_spreadsheet()
        filename = f"lessons_{user_id}_{datetime.now().strftime('%d-%m-%Y_%H:%M')}.xlsx"
        await container.upload_blob(
            filename,
            data.file,
            content_settings=ContentSettings(content_type=data.file.content_type),
        )
        async with function_session() as client:
            res = await client.post(
                "/api/lesson/upload-spreadsheet",
                json={"filename": filename, "instructor_id": str(user_id)},
            )
            res_json = await res.json()
        if res.ok:
            if res_json.get("course_id") and res_json.get("term_id"):
                course = session.get(Course, UUID(res_json["course_id"]))
                term = session.exec(
                    select(CourseTerm)
                    .options(selectinload(CourseTerm.lessons))
                    .where(CourseTerm.id == UUID(res_json["term_id"]))
                ).first()
                if course and term:
                    return term
                else:
                    logging.error("The term lesson was not created")
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                logging.error(
                    "The keys 'course_id' and 'term_id' was not set on function response"  # noqa: E501
                )
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            logging.error("function error: " + res_json["message"])
            return JSONResponse(
                status_code=res.status,
                content={
                    "detail": {
                        "message": res_json["message"],
                        "errors": res_json.get("errors", []),
                        "state_error": res_json.get("state_error"),
                    }
                },
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
    response_model_relationship={
        "get": {"instructor", "term"},
        "update": {"instructor", "term"},
    },
    router=router,
)
