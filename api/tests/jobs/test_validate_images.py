from random import random

import pytest

from api.jobs.validate_images import Validator, run


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


async def test_validation(
    session, validator, user_password, lesson, lesson_user, factory
):
    validations = await factory.list_lesson_validation(
        10, session, user_password, lesson, lesson_user
    )
    lesson_user_validated = await factory.lesson_user(
        session, user_password, lesson, validated=True, validated_success=False
    )
    validations_validated = await factory.list_lesson_validation(
        10,
        session,
        user_password,
        lesson,
        lesson_user_validated,
        validated=True,
        validated_success=False,
    )
    await run(validator)
    await session.refresh(lesson_user)
    await session.refresh(lesson_user_validated)
    assert lesson_user.validated
    assert lesson_user.validated_success
    for validation in validations:
        await session.refresh(validation)
        assert validation.validated
        assert validation.validated_success
        assert validation.validated_value == validator.get_confidence(validation)
    assert lesson_user_validated.validated
    assert not lesson_user_validated.validated_success
    for validation in validations_validated:
        await session.refresh(validation)
        assert validation.validated
        assert not validation.validated_success
        assert not validation.validated_value


async def test_validate_only_one(
    session, validator, user_password, lesson, lesson_user, lesson_validation, factory
):
    validations_validated = await factory.list_lesson_validation(
        10,
        session,
        user_password,
        lesson,
        lesson_user,
        validated=True,
        validated_success=False,
    )
    await run(validator)
    await session.refresh(lesson_user)
    await session.refresh(lesson_validation)
    assert lesson_user.validated
    assert not lesson_user.validated_success
    assert lesson_validation.validated
    assert lesson_validation.validated_success
    assert lesson_validation.validated_value == validator.get_confidence(
        lesson_validation
    )
    for validation in validations_validated:
        await session.refresh(validation)
        assert validation.validated
        assert not validation.validated_success
        assert not validation.validated_value
