
import re
from typing import Annotated
from http import HTTPStatus
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException
from sqlalchemy import text

from api.models import Session, Lesson, MediaType, LessonValidation
from api.dto import ValidationIn
from api.aws import get_container_image
from api.auth import LoggedUserId

router = APIRouter(
    prefix="/validation",
    tags=["validation"]
)

@router.post("/create", status_code=HTTPStatus.CREATED)
def create(data: Annotated[ValidationIn, Form()], user_id: LoggedUserId):
    match = re.fullmatch(r'(\w+)/(\w+)', data.file.content_type.lower())
    mime_types = {
        "image": MediaType.IMAGE,
        "video": MediaType.VIDEO
    }
    extensions = ['png', 'jpeg', 'jpg']
    if match:
        mime_type, media_type = match.groups()
        if mime_type not in mime_types or media_type not in extensions:
            raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        mime_type_enum = MediaType(mime_type.upper())
    else:
        raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    with Session() as session:
        lesson = session.get(Lesson, data.lesson_id)
        if lesson:
            pass
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

