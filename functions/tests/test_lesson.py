from datetime import datetime, date, time

import pytest
import mimesis
from sqlmodel import select

from api import models
from functions.lessons_parser import LessonParserResult, LessonItem
from functions.lesson import create_lessons


@pytest.fixture
def course_term(session, user_password):
    with session.begin():
        user_password[0].role = models.UserRole.INSTRUCTOR
        session.add(user_password[0])
        text = mimesis.Text()
        course = models.Course(
            name=text.title(),
            description=text.sentence(),
        )
        session.add(course)
        dt = mimesis.Datetime()
        term = models.CourseTerm(
            term_number=1,
            status=models.TermStatus.WAITING,
            start_date=dt.date(),
            end_date=dt.date(),
            course=course,
        )
        session.add(term)
        session.add(
            models.TermUser(
                user_id=user_password[0].id,
                term_id=term.id,
                role=models.UserRole.INSTRUCTOR,
            )
        )
        return course, term


@pytest.fixture
def parser_result(course_term, user_password):
    course, term = course_term
    text = mimesis.Text()
    num = mimesis.Numeric()
    lesson = LessonItem(
        title=text.title(),
        start_date=date.today(),
        start_time=time(hour=8),
        duration_min=num.integer_number(30, 120),
        description=text.quote(),
        instructor=user_password[0].username,
        line_number=num.integer_number(0, 10),
    )
    return LessonParserResult(
        course_name=course.name, term_number=term.term_number, lessons=[lesson]
    )


def test_create_one_lesson(session, user_password, course_term, parser_result):
    course, term = course_term
    lesson = parser_result.lessons[0]
    result = create_lessons(parser_result, user_password[0].id)
    session.refresh(course)
    session.refresh(term)
    assert not result.errors
    assert result.course_id == course.id
    assert result.term_id == term.id
    assert len(term.lessons) == 1
    assert term.lessons[0].title == lesson.title
    assert term.lessons[0].description == lesson.description
    assert term.lessons[0].start_date == datetime.combine(
        lesson.start_date, lesson.start_time
    )
    assert term.lessons[0].duration_min == lesson.duration_min
    assert term.lessons[0].instructor_id == user_password[0].id


def test_instructor_not_found(session, user_password, course_term, parser_result):
    text = mimesis.Text()
    num = mimesis.Numeric()
    lesson = LessonItem(
        title=text.title(),
        start_date=date.today(),
        start_time=time(hour=8),
        duration_min=num.integer_number(30, 120),
        description=text.quote(),
        instructor="wrong instructor. this instructor doesn't exist",
        line_number=num.integer_number(0, 10),
    )
    parser_result.lessons.append(lesson)
    result = create_lessons(parser_result, user_password[0].id)
    assert not result.course_id
    assert not result.term_id
    assert len(result.errors) == 1
    assert result.errors[0][0] == lesson.line_number
    assert "not found" in result.errors[0][1]
    assert not len(session.exec(select(models.Lesson)).all())
