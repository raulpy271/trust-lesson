from typing import Annotated
from http import HTTPStatus
from uuid import uuid4

from sqlmodel import select
from fastapi import APIRouter, Form, HTTPException
from azure.storage.blob import ContentSettings

from api.models import Lesson, LessonUser, MediaType, LessonValidation
from api.dto import ValidationIn
from api.azure.storage import get_container_image
from api.depends import LoggedUserId, SessionDep
from api.utils import parse_content_type

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post(
    "/create",
    status_code=HTTPStatus.CREATED,
    response_model=LessonValidation.response_model(),
)
async def create(
    data: Annotated[ValidationIn, Form()], user_id: LoggedUserId, session: SessionDep
):
    mime_type, media_type = parse_content_type(data.file.content_type)
    mime_type_enum = MediaType(mime_type.upper())
    lesson = session.get(Lesson, data.lesson_id)
    if lesson:
        lesson_user = session.exec(
            select(LessonUser).where(
                LessonUser.lesson_id == lesson.id, LessonUser.user_id == user_id
            )
        ).one_or_none()
        if lesson_user:
            validation_id = uuid4()
            key = f"{validation_id}.{media_type}"
            container = get_container_image()
            await container.upload_blob(
                key,
                data.file,
                content_settings=ContentSettings(content_type=data.file.content_type),
            )
            validation = LessonValidation(
                lesson_id=lesson.id,
                user_id=user_id,
                media_path=key,
                media_type=mime_type_enum,
                lesson_user=lesson_user,
            )
            session.add(validation)
            session.commit()
            session.refresh(validation)
            return validation
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
