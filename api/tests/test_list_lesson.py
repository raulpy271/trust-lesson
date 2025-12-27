from datetime import datetime, timedelta
from http import HTTPStatus

from api.models import UserRole
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


async def test_filter_by_date(
    client, user_password, token, session, course_term, factory
):
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=1)).date()
    # lessons inside filter
    lessons_to_include = await factory.list_lesson(
        3, session, course_term, user_password, start_date=datetime.now()
    )
    # lessons outside filter
    lessons_to_exclude = await factory.list_lesson(
        3,
        session,
        course_term,
        user_password,
        start_date=datetime(year=2022, month=2, day=1),
    )
    [
        await factory.lesson_user(session, user_password, lesson)
        for lesson in lessons_to_include + lessons_to_exclude
    ]
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


async def test_filter_by_logged_user(client, session, course_term, factory):
    user_password1 = await factory.user_password(session)
    user_password2 = await factory.user_password(session)
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=1)).date()
    (lesson_user1, lesson_user2) = await factory.list_lesson(
        2, session, course_term, user_password1, start_date=datetime.now()
    )
    await factory.lesson_user(session, user_password1, lesson_user1)
    await factory.lesson_user(session, user_password2, lesson_user2)
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


async def test_list_lessons_of_instructor(
    client, user_password, token, session, course_term, lesson, factory
):
    user, _ = user_password
    # Register user as instructor of the lesson
    user.role = UserRole.INSTRUCTOR
    lesson.instructor = user
    lesson.start_date = datetime.now()
    # Create lesson when the user is not the instructor
    user_password2 = await factory.user_password(session)
    lesson2 = await factory.lesson(
        session, course_term, user_password2, start_date=datetime.now()
    )
    await factory.lesson_user(session, user_password2, lesson2)
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


async def test_students_of_a_lesson(
    client, user_password, token, session, course_term, lesson, factory
):
    students_with_passwords = await factory.list_user_password(5, session)
    [
        await factory.term_user(session, course_term, student)
        for student in students_with_passwords
    ]
    await factory.term_user(
        session, course_term, user_password, role=UserRole.INSTRUCTOR
    )
    [
        await factory.lesson_user(session, student, lesson)
        for student in students_with_passwords
    ]
    await factory.lesson_user(session, user_password, lesson)
    response = client.get(f"/logged/lesson/student/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.OK
    students_resp = response.json()
    students_map = {str(up[0].id): up[0] for up in students_with_passwords}
    assert len(students_with_passwords) == len(students_resp)
    for student_resp in students_resp:
        assert student_resp["id"] in students_map
        student = students_map[student_resp["id"]]
        assert student_resp["username"] == student.username
        assert student_resp["email"] == student.email


async def test_instructor_of_a_lesson(
    client, token, session, course_term, lesson, factory
):
    instructors_with_passwords = await factory.list_user_password(
        3, session, role=UserRole.INSTRUCTOR
    )
    main_instructor = instructors_with_passwords[0][0]
    lesson.instructor = main_instructor
    session.add(lesson)
    await session.commit()
    students_with_passwords = await factory.list_user_password(5, session)
    [
        await factory.term_user(session, course_term, user, role=user[0].role)
        for user in students_with_passwords + instructors_with_passwords
    ]
    [
        await factory.lesson_user(session, student, lesson)
        for student in students_with_passwords + instructors_with_passwords
    ]
    response = client.get(f"/logged/lesson/instructor/{lesson.id}", auth=token)
    assert response.status_code == HTTPStatus.OK
    instructors_resp = response.json()
    assert instructors_resp["main"]["id"] == str(main_instructor.id)
    assert instructors_resp["main"]["username"] == str(main_instructor.username)
    assert len(instructors_resp["instructors"]) == len(instructors_with_passwords)
    instructors_map = {str(up[0].id): up[0] for up in instructors_with_passwords}
    for instructor_resp in instructors_resp["instructors"]:
        assert instructor_resp["id"] in instructors_map
        instructor = instructors_map[instructor_resp["id"]]
        assert instructor_resp["username"] == instructor.username
        assert instructor_resp["email"] == instructor.email
