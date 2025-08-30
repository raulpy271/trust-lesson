from datetime import datetime, timedelta
from http import HTTPStatus

from api import models
from tests.factories import factory
from tests.utils import authenticate


def test_list_one_lesson(client, user_password, token, session, lesson, lesson_user):
    start_date = lesson.start_date.date()
    end_date = (lesson.start_date + timedelta(days=1)).date()
    response = client.get(
        "/logged/lesson/list",
        auth=token,
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == HTTPStatus.OK
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["id"] == str(lesson.id)


def test_filter_by_date(client, user_password, token, session, course_term):
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=1)).date()
    # lessons inside filter
    lessons_to_include = factory.list_lesson(
        3, session, course_term, user_password, start_date=datetime.now()
    )
    # lessons outside filter
    lessons_to_exclude = factory.list_lesson(
        3,
        session,
        course_term,
        user_password,
        start_date=datetime(year=2022, month=2, day=1),
    )
    [
        factory.lesson_user(session, user_password, lesson)
        for lesson in lessons_to_include + lessons_to_exclude
    ]
    session.commit()
    response = client.get(
        "/logged/lesson/list",
        auth=token,
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == HTTPStatus.OK
    lessons = response.json()
    assert len(lessons) == len(lessons_to_include)
    to_include_ids = [str(lesson.id) for lesson in lessons_to_include]
    for lesson in lessons:
        assert lesson["id"] in to_include_ids


def test_filter_by_logged_user(client, session, course_term):
    user_password1 = factory.user_password(session)
    user_password2 = factory.user_password(session)
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=1)).date()
    (lesson_user1, lesson_user2) = factory.list_lesson(
        2, session, course_term, user_password1, start_date=datetime.now()
    )
    factory.lesson_user(session, user_password1, lesson_user1)
    factory.lesson_user(session, user_password2, lesson_user2)
    # authenticate with user 1
    t = authenticate(client, user_password1[0], user_password1[1])
    # Request lessons of user 1
    response = client.get(
        "/logged/lesson/list",
        auth=t,
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == HTTPStatus.OK
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["id"] == str(lesson_user1.id)
    # authenticate with user 2
    t = authenticate(client, user_password2[0], user_password2[1])
    # Request lessons of user 2
    response = client.get(
        "/logged/lesson/list",
        auth=t,
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == HTTPStatus.OK
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["id"] == str(lesson_user2.id)


def test_list_lessons_of_instructor(
    client, user_password, token, session, course_term, lesson
):
    user, _ = user_password
    # Register user as instructor of the lesson
    user.role = models.UserRole.INSTRUCTOR
    lesson.instructor = user
    lesson.start_date = datetime.now()
    # Create lesson when the user is not the instructor
    user_password2 = factory.user_password(session)
    lesson2 = factory.lesson(
        session, course_term, user_password2, start_date=datetime.now()
    )
    factory.lesson_user(session, user_password2, lesson2)
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=1)).date()
    response = client.get(
        "/logged/lesson/list",
        auth=token,
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == HTTPStatus.OK
    lessons = response.json()
    assert len(lessons) == 1
    assert lessons[0]["id"] == str(lesson.id)
