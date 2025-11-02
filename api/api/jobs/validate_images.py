from sqlmodel import select, not_
from sqlalchemy.orm import selectinload

from api.utils import format_traceback
from api.models import AsyncSession, LessonUser, LessonValidation


class Validator:
    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError

    async def get_confidence(self, validation: LessonValidation) -> float:
        raise NotImplementedError


async def run(validator: Validator):
    async with AsyncSession() as session, validator:
        lesson_users = await session.exec(
            select(LessonUser)
            .options(selectinload(LessonUser.validations))
            .where(not_(LessonUser.validated))
        )
        for lesson_user in lesson_users:
            validated_count = 0
            validated_success_count = 0
            for validation in lesson_user.validations:
                if not validation.validated:
                    try:
                        confidence = await validator.get_confidence(validation)
                        validation.validated_success = True
                        validation.confidence = confidence
                        validated_success_count += 1
                    except Exception as e:
                        validation.validated_success = False
                        validation.error_message = str(e)
                        validation.error_traceback = format_traceback(e)
                    validation.validated = True
                    validated_count += 1
                else:
                    validated_count += 1
                    if validation.validated_success:
                        validated_success_count += 1

            lesson_user.validated = validated_count == len(lesson_user.validations)
            lesson_user.validated_success = validated_success_count == len(
                lesson_user.validations
            )
        await session.commit()
