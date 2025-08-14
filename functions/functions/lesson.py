from datetime import datetime
import logging
from io import BytesIO
from typing import Optional
from uuid import UUID

import pandas
from sqlalchemy import select
from pydantic import BaseModel

from api.models import Session, User, UserRole, TermUser, Course, CourseTerm, Lesson
from api.azure.storage import get_container_spreadsheet
from functions.lessons_parser import LessonParserResult


class CreateLessonsResult(BaseModel):
    course_id: Optional[UUID] = None
    term_id: Optional[UUID] = None
    errors: list[tuple[int, str]] = []


async def read_df_from_storage(filename):
    container = get_container_spreadsheet()
    stream = await container.download_blob(filename)
    file = BytesIO()
    await stream.readinto(file)
    logging.info(f"file {filename} downloaded")
    return pandas.read_excel(file)


def create_lessons(
    lessons: LessonParserResult, instructor_id: UUID
) -> CreateLessonsResult:
    errors = []
    with Session() as session:
        course = session.execute(
            select(
                Course.id,
                Course.name,
                CourseTerm.id.label("term_id"),
                CourseTerm.term_number,
            )
            .join(Course.terms)
            .where(
                (Course.name == lessons.course_name)
                & (CourseTerm.term_number == lessons.term_number)
            )
        ).one()
        instructors = session.execute(
            select(User.id, User.username)
            .join(TermUser)
            .where(
                (User.role == UserRole.INSTRUCTOR)
                & (TermUser.term_id == course.term_id)
            )
        ).all()
    try:
        with Session() as session, session.begin():
            for lesson in lessons.lessons:
                instructor = instructor_id
                if lesson.instructor:
                    try:
                        instructor = next(
                            filter(
                                lambda i: i.username == lesson.instructor, instructors
                            )
                        )
                        instructor = instructor.id
                    except StopIteration:
                        errors.append(
                            (
                                lesson.line_number,
                                f"Instructor '{lesson.instructor}' not found",
                            )
                        )
                        continue
                session.add(
                    Lesson(
                        title=lesson.title,
                        duration_min=lesson.duration_min,
                        description=lesson.description,
                        start_date=datetime.combine(
                            lesson.start_date, lesson.start_time
                        ),
                        term_id=course.term_id,
                        instructor_id=instructor,
                    )
                )
            if not errors:
                return CreateLessonsResult(course_id=course.id, term_id=course.term_id)
            else:
                raise Exception("Error when creating lessons")
    except Exception as e:
        if errors:
            return CreateLessonsResult(errors=errors)
        else:
            return CreateLessonsResult(errors=(0, str(e)))
