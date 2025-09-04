from uuid import UUID
from http import HTTPStatus

from api import models
from tests.factories import factory


def test_get_course_term(client, token, course_term):
    response = client.get(f"/logged/course-term/{course_term.id}", auth=token)
    assert response.status_code == HTTPStatus.OK
    term = response.json()
    assert str(course_term.id) == term["id"]
    assert str(course_term.course_id) == term["course_id"]
    assert str(course_term.start_date) == term["start_date"]
    assert str(course_term.end_date) == term["end_date"]


async def test_create_course_term(client, token, session, course, admin):
    create = {
        "status": "FINISHED",
        "start_date": "2025-01-01",
        "end_date": "2025-06-01",
        "course_id": str(course.id),
    }
    response = client.post("/logged/course-term/", auth=token, json=create)
    assert response.status_code == HTTPStatus.CREATED
    created = response.json()
    for k, v in create.items():
        assert created[k] == v
    term = await session.get(models.CourseTerm, UUID(created["id"]))
    assert term
    assert term.term_number == 0
    assert term.course.id == course.id


async def test_create_course_term_number(client, token, session, course, admin):
    i = 0
    for i in range(4):
        create = {
            "status": "FINISHED",
            "start_date": "2025-01-01",
            "end_date": "2025-06-01",
            "course_id": str(course.id),
        }
        response = client.post("/logged/course-term/", auth=token, json=create)
        assert response.status_code == HTTPStatus.CREATED
        created = response.json()
        assert created["term_number"] == i
        await session.refresh(course)
        assert course.terms_count == i + 1
    course2 = await factory.course(session)
    create = {
        "status": "FINISHED",
        "start_date": "2025-01-01",
        "end_date": "2025-06-01",
        "course_id": str(course2.id),
    }
    response = client.post("/logged/course-term/", auth=token, json=create)
    assert response.status_code == HTTPStatus.CREATED
    created = response.json()
    assert created["term_number"] == 0
    await session.refresh(course)
    await session.refresh(course2)
    assert course.terms_count == i + 1
    assert course2.terms_count == 1


async def test_delete_course_term_number(client, token, session, course, admin):
    count = 5
    terms = await factory.list_course_term(count, session, course)
    id_delete = terms[0].id
    await session.refresh(course)
    assert course.terms_count == count
    response = client.delete(f"/logged/course-term/{id_delete}", auth=token, params={})
    assert response.status_code == HTTPStatus.OK
    await session.refresh(course)
    assert course.terms_count == count - 1
    session.expire_all()
    assert not await session.get(models.CourseTerm, id_delete)
