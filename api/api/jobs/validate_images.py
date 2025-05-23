from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.models import Session, LessonUser, LessonValidation


class Validator:
    def __call__(self, validation: LessonValidation) -> float:
        raise NotImplementedError


def run(validator: Validator):
    with Session() as session:
        lesson_users = session.scalars(
            select(LessonUser)
            .options(selectinload(LessonUser.validations))
            .where(~LessonUser.validated)
        )
        for lesson_user in lesson_users:
            validated_count = 0
            validated_success_count = 0
            for validation in lesson_user.validations:
                if not validation.validated:
                    try:
                        confidence = validator(validation)
                        validation.validated_success = True
                        validation.validated_value = confidence
                        validated_success_count += 1
                    except Exception:
                        validation.validated_success = False
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
        session.commit()
