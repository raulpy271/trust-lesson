from uuid import UUID
from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, AfterValidator
from fastapi import UploadFile

from api.models import IdentityValidation, UserIdentity, IdentityType
from api.utils import check_media_type, compare_code


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


class IdentityComparisonOut(BaseModel):
    identity_code: str
    identity_code_doc: Optional[str]
    identity_code_confidence: Optional[float]

    type: IdentityType
    type_doc: Optional[IdentityType]
    type_confidence: Optional[float]

    fullname: str
    fullname_doc: Optional[str]
    fullname_confidence: Optional[float]

    parent_fullname: Optional[str]
    parent_fullname_doc: Optional[str]
    parent_fullname_confidence: Optional[float]

    birth_date: date
    birth_date_doc: Optional[date]
    birth_date_confidence: Optional[float]

    expiration_date: date
    expiration_date_doc: Optional[date]
    expiration_date_confidence: Optional[float]

    issued_date: Optional[date]
    issued_date_doc: Optional[date]
    issued_date_confidence: Optional[float]

    issuing_authority: Optional[str]
    issuing_authority_doc: Optional[str]
    issuing_authority_confidence: Optional[float]

    country_state: Optional[str]
    country_state_doc: Optional[str]
    country_state_confidence: Optional[float]

    not_match_fields: list[str]
    not_found_fields: list[str]

    @staticmethod
    def create(
        identity: UserIdentity, validation: IdentityValidation
    ) -> "IdentityComparisonOut":
        fields = [
            "type",
            "fullname",
            "parent_fullname",
            "birth_date",
            "expiration_date",
            "issued_date",
            "issuing_authority",
            "country_state",
        ]
        args = {
            "identity_code": identity.identity_code,
            "identity_code_doc": validation.identity_code,
            "identity_code_confidence": validation.identity_code_confidence,
            "not_match_fields": [],
            "not_found_fields": [],
        }
        if validation.identity_code:
            if not compare_code(identity.identity_code, validation.identity_code):
                args["not_match_fields"].append("identity_code")
        else:
            args["not_found_fields"].append("identity_code")
        for field in fields:
            args[field] = getattr(identity, field)
            args[field + "_doc"] = getattr(validation, field)
            args[field + "_confidence"] = getattr(validation, field + "_confidence")
            if getattr(validation, field):
                if getattr(identity, field):
                    if getattr(identity, field) != getattr(validation, field):
                        args["not_match_fields"].append(field)
            else:
                args["not_found_fields"].append(field)
        return IdentityComparisonOut(**args)
