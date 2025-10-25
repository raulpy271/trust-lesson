from datetime import date
from uuid import uuid4

from api.models import UserIdentity, IdentityValidation, IdentityType
from api.dto import IdentityComparisonOut


def test_create_identity_comparison():
    ui = UserIdentity(
        id=uuid4(),
        user_id=uuid4(),
        identity_code="101.123.432-34",
        type=IdentityType.IDENTITY_CARD,
        fullname="Leonel Salamanca",
        birth_date=date(year=2000, month=3, day=1),
        expiration_date=date(year=2025, month=1, day=1),
        issued_date=date(year=2025, month=1, day=1),
    )
    iv = IdentityValidation(
        id=uuid4(),
        user_id=uuid4(),
        validated=True,
        validated_success=True,
        image_path="/test.jpg",
        identity_code="101.123.43234",
        identity_code_confidence=0.7,
        type=IdentityType.IDENTITY_CARD,
        fullname="Leonel Salamanca",
        parent_fullname="Hector Salamanca",
        type_confidence=0.7,
        birth_date=date(year=2001, month=3, day=1),
        birth_date_confidence=0.6,
        issued_date=date(year=2025, month=1, day=1),
        issued_date_confidence=0.6,
    )
    comp = IdentityComparisonOut.create(ui, iv)
    assert comp.not_found_fields == [
        "expiration_date",
        "issuing_authority",
        "country_state",
    ]
    assert comp.not_match_fields == ["birth_date"]
    assert comp.identity_code == ui.identity_code
    assert comp.identity_code_doc == iv.identity_code
    assert comp.identity_code_confidence == iv.identity_code_confidence
    assert comp.birth_date == ui.birth_date
    assert comp.birth_date_doc == iv.birth_date
    assert comp.birth_date_confidence == iv.birth_date_confidence
