from typing import Annotated
from http import HTTPStatus
from uuid import uuid4

from sqlalchemy import select
from fastapi import APIRouter, Form, HTTPException
from azure.storage.blob import ContentSettings

from api.models import Session, Lesson, LessonUser, MediaType, LessonValidation
from api.dto import ValidationIn
from api import azure
from api.auth import LoggedUserId
from api.utils import parse_content_type

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/create", status_code=HTTPStatus.CREATED)
async def create(data: Annotated[ValidationIn, Form()], user_id: LoggedUserId):
    mime_type, media_type = parse_content_type(data.file.content_type)
    mime_type_enum = MediaType(mime_type.upper())
    with Session() as session:
        lesson = session.get(Lesson, data.lesson_id)
        if lesson:
            lesson_user = session.scalars(
                select(LessonUser).where(
                    LessonUser.lesson_id == lesson.id and LessonUser.user_id == user_id
                )
            ).one_or_none()
            if lesson_user:
                validation_id = uuid4()
                key = f"{validation_id}.{media_type}"
                container = azure.get_container_image()
                await container.upload_blob(
                    key,
                    data.file,
                    content_settings=ContentSettings(
                        content_type=data.file.content_type
                    ),
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
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
