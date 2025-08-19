from uuid import UUID
from http import HTTPStatus

import mimesis

from api import models
from tests.factories import factory


def test_only_admin_can_create_course(client, token):
    text = mimesis.Text()
    create = {"name": text.title(), "description": text.sentence()}
    response = client.post("/logged/course/", auth=token, json=create)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_course(client, token, session, admin):
    text = mimesis.Text()
    create = {"name": text.title(), "description": text.sentence()}
    response = client.post("/logged/course/", auth=token, json=create)
    assert response.status_code == HTTPStatus.CREATED
    created = response.json()
    print(created)
    assert create["name"] == created["name"]
    assert create["description"] == created["description"]
    assert created.get("id")
    course = session.get(models.Course, UUID(created["id"]))
    assert course.name == create["name"]
    assert course.description == create["description"]
    assert course.terms_count == 0


def test_list_course(client, token, session):
    courses = factory.list_course(3, session)
    response = client.get("/logged/course/", auth=token)
    assert response.status_code == HTTPStatus.OK
    courses_res = response.json()
    assert len(courses) == len(courses_res)
    for course, course_res in zip(courses, courses_res):
        assert course.name == course_res["name"]
        assert course.description == course_res["description"]


def test_update_course(client, token, session, admin, course):
    text = mimesis.Text()
    update = {"name": course.name, "description": text.sentence()}
    response = client.put(f"/logged/course/{course.id}", auth=token, json=update)
    assert response.status_code == HTTPStatus.OK
    updated = response.json()
    assert course.name == updated["name"]
    assert course.description != updated["description"]
    session.refresh(course)
    assert course.description == updated["description"]
    assert course.description == update["description"]


def test_update_course_not_found(client, token, admin):
    text = mimesis.Text()
    crypto = mimesis.Cryptographic()
    update = {"name": text.title(), "description": text.sentence()}
    response = client.put(f"/logged/course/{crypto.uuid()}", auth=token, json=update)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_course(client, token, admin, course, session):
    course_id = course.id
    response = client.delete(f"/logged/course/{course.id}", auth=token, params={})
    assert response.status_code == HTTPStatus.OK
    session.expire_all()
    assert not session.get(models.Course, course_id)


def test_delete_course_not_found(client, token, admin):
    crypto = mimesis.Cryptographic()
    response = client.delete(f"/logged/course/{crypto.uuid()}", auth=token, params={})
    assert response.status_code == HTTPStatus.NOT_FOUND
