from datetime import datetime
from typing import Annotated
from http import HTTPStatus
from uuid import UUID, uuid4
import logging

from sqlmodel import select
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Form, HTTPException
from azure.storage.blob import ContentSettings

from api.models import (
    Lesson,
    LessonUser,
    MediaType,
    LessonValidation,
    IdentityValidation,
)
from api.dto import LessonValidationIn, IdentityValidationIn, IdentityComparisonOut
from api.azure.functions import function_session
from api.azure.storage import get_container_image
from api.models import User
from api.depends import LoggedUserId, SessionDep
from api.utils import parse_content_type

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post(
    "/lesson",
    status_code=HTTPStatus.CREATED,
    response_model=LessonValidation.response_model(),
)
async def lesson_create(
    data: Annotated[LessonValidationIn, Form()],
    user_id: LoggedUserId,
    session: SessionDep,
):
    mime_type, media_type = parse_content_type(data.file.content_type)
    mime_type_enum = MediaType(mime_type.upper())
    lesson = await session.get(Lesson, data.lesson_id)
    if lesson:
        result = await session.exec(
            select(LessonUser).where(
                LessonUser.lesson_id == lesson.id, LessonUser.user_id == user_id
            )
        )
        lesson_user = result.one_or_none()
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
            await session.commit()
            await session.refresh(validation)
            return validation
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post(
    "/identity",
    status_code=HTTPStatus.CREATED,
    response_model=IdentityComparisonOut,
)
async def identity_create(
    data: Annotated[IdentityValidationIn, Form()],
    user_id: LoggedUserId,
    session: SessionDep,
):
    _, media_type = parse_content_type(data.file.content_type)
    try:
        user = await session.get(User, user_id, options=[selectinload(User.identity)])
        if user.identity:
            key_datetime = datetime.now().strftime("%d-%m-%Y_%H:%M")
            key = f"identity-validation-{user_id}-{key_datetime}.{media_type}"
            container = get_container_image()
            await container.upload_blob(
                key,
                data.file,
                content_settings=ContentSettings(content_type=data.file.content_type),
            )
            async with function_session() as client:
                res = await client.post(
                    "/api/validation/user-identity",
                    json={"filename": key, "user_id": str(user_id)},
                )
                res_json = await res.json()
            if res.ok:
                validation = await session.get(IdentityValidation, UUID(res_json["id"]))
                comparison = IdentityComparisonOut.create(user.identity, validation)
                return comparison
            else:
                message = res_json.get("error_message") or res_json.get("message")
                logging.error(f"Error when validating identity of user {user_id}")
                logging.error(message)
                validated = res_json.get("validated")
                model = None
                if validated:
                    validation = await session.get(
                        IdentityValidation, UUID(res_json["id"])
                    )
                    model = validation.model_dump()
                raise HTTPException(
                    status_code=res.status,
                    detail={
                        "message": message,
                        "validation": model,
                    },
                )
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail={
                    "message": "The user doesn't have an identity to be validated.",
                    "validation": None,
                },
            )
    except Exception as e:
        logging.error(str(e))
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR)
