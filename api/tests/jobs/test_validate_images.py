from random import random

import pytest

from api.jobs.validate_images import Validator, run
from tests.factories import factory


@pytest.fixture
def validator():
    class DummyValidator(Validator):
        def __init__(self):
            self.values = {}

        def __call__(self, validation):
            self.values[validation.id] = random()
            return self.values[validation.id]

        def get_confidence(self, validation):
            return self.values[validation.id]

    return DummyValidator()


def test_validation(session, validator, user_password, lesson, lesson_user):
    validations = factory.list_lesson_validation(
        10, session, user_password, lesson, lesson_user
    )
    lesson_user_validated = factory.lesson_user(
        session, user_password, lesson, validated=True, validated_success=False
    )
    validations_validated = factory.list_lesson_validation(
        10,
        session,
        user_password,
        lesson,
        lesson_user_validated,
        validated=True,
        validated_success=False,
    )
    run(validator)
    session.refresh(lesson_user)
    session.refresh(lesson_user_validated)
    assert lesson_user.validated
    assert lesson_user.validated_success
    for validation in validations:
        session.refresh(validation)
        assert validation.validated
        assert validation.validated_success
        assert validation.validated_value == validator.get_confidence(validation)
    assert lesson_user_validated.validated
    assert not lesson_user_validated.validated_success
    for validation in validations_validated:
        session.refresh(validation)
        assert validation.validated
        assert not validation.validated_success
        assert not validation.validated_value


def test_validate_only_one(
    session, validator, user_password, lesson, lesson_user, lesson_validation
):
    validations_validated = factory.list_lesson_validation(
        10,
        session,
        user_password,
        lesson,
        lesson_user,
        validated=True,
        validated_success=False,
    )
    run(validator)
    session.refresh(lesson_user)
    session.refresh(lesson_validation)
    assert lesson_user.validated
    assert not lesson_user.validated_success
    assert lesson_validation.validated
    assert lesson_validation.validated_success
    assert lesson_validation.validated_value == validator.get_confidence(
        lesson_validation
    )
    for validation in validations_validated:
        session.refresh(validation)
        assert validation.validated
        assert not validation.validated_success
        assert not validation.validated_value
