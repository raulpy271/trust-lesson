from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, AfterValidator
from fastapi import UploadFile

from api.utils import check_media_type


class LessonValidationIn(BaseModel):
    lesson_id: UUID
    file: Annotated[
        UploadFile,
        AfterValidator(
            check_media_type(["png", "jpeg", "jpg"], mime_types=["image", "video"])
        ),
    ]


class IdentityValidationIn(BaseModel):
    file: Annotated[
        UploadFile,
        AfterValidator(check_media_type(["png", "jpeg", "jpg"], mime_types=["image"])),
    ]
