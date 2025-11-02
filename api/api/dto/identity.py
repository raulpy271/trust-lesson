from uuid import UUID
from typing import Optional
from datetime import date

from pydantic import BaseModel

from api.models import IdentityType


class CreateUserIdentityIn(BaseModel):
    user_id: UUID
    identity_code: str
    type: IdentityType
    fullname: str
    parent_fullname: Optional[str]
    birth_date: date
    expiration_date: date
    issued_date: Optional[date]
    issuing_authority: Optional[str]
    country_state: Optional[str]
