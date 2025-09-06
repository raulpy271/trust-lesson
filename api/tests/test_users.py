from hashlib import scrypt
from http import HTTPStatus

import mimesis
from sqlmodel import select

from api import settings
from api.models import User
from tests.factories import factory


async def test_create(session, client, token):
    person = mimesis.Person()
    user = {
        "username": person.username(),
        "fullname": person.full_name(),
        "email": person.email(),
        "password": person.password(),
    }
    resp = client.post("logged/user/", json=user, auth=token)
    assert resp.status_code == HTTPStatus.CREATED
    u = (
        await session.exec(select(User).where(User.username == user["username"]))
    ).one()
    assert u.fullname == user["fullname"]
    assert u.email == user["email"]
    phash = scrypt(
        user["password"].encode("utf-8"),
        salt=u.password_salt.encode("utf-8"),
        **settings.SCRYPT_SETTINGS,
    )
    assert u.password_hash == phash.hex()


def test_exclude_columns(client, token, user_password):
    user = user_password[0]
    response = client.get("/logged/user/me", auth=token)
    result = response.json()
    assert isinstance(result, dict)
    assert str(user.id) == result["id"]
    assert user.username == result["username"]
    assert user.fullname == result["fullname"]
    assert user.email == result["email"]
    assert not result.get("password")
    assert not result.get("password_hash")
    assert not result.get("password_salt")


async def test_list_users(client, token, session, user_password, admin):
    logged_user, _ = user_password
    users = [logged_user] + [
        users_password[0]
        for users_password in await factory.list_user_password(3, session)
    ]
    response = client.get("/logged/user/", auth=token)
    assert response.status_code == HTTPStatus.OK
    users_res = response.json()
    assert len(users) == len(users_res)
    for user, user_res in zip(users, users_res):
        assert user.username == user_res["username"]
        assert user.email == user_res["email"]
        assert user.is_admin == user_res["is_admin"]


async def test_update_user(client, session, token, user_password, admin):
    person = mimesis.Person()
    update = {
        "username": user_password[0].username,
        "fullname": person.full_name(),
        "email": user_password[0].email,
        "is_admin": not user_password[0].is_admin,
        "role": user_password[0].role,
        "password": user_password[1],
    }
    response = client.put(f"logged/user/{user_password[0].id}", json=update, auth=token)
    assert response.status_code == HTTPStatus.OK
    user = user_password[0]
    await session.refresh(user)
    assert user.username == update["username"]
    assert user.fullname == update["fullname"]
    assert user.email == update["email"]


async def test_user_cannot_promote_himself_to_admin(
    client, session, token, user_password
):
    person = mimesis.Person()
    update = {
        "username": user_password[0].username,
        "fullname": person.full_name(),
        "email": user_password[0].email,
        "is_admin": True,
        "role": user_password[0].role,
        "password": user_password[1],
    }
    response = client.put(f"logged/user/{user_password[0].id}", json=update, auth=token)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    user = await session.get(User, user_password[0].id)
    assert not user.is_admin


async def test_user_cannot_delete_another(client, session, token, user_password):
    user_id = (await factory.user_password(session))[0].id
    response = client.delete(
        f"/logged/user/{user_id}", auth=token, params={"password": user_password[1]}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_user_can_delete_itself(client, token, session, user_password):
    user_id = user_password[0].id
    response = client.delete(
        f"/logged/user/{user_id}", auth=token, params={"password": user_password[1]}
    )
    assert response.status_code == HTTPStatus.OK
    session.expire_all()
    assert not await session.get(User, user_id)


async def test_admin_can_delete_anyone(client, token, session, user_password, admin):
    user_id = (await factory.user_password(session))[0].id
    response = client.delete(
        f"/logged/user/{user_id}", auth=token, params={"password": user_password[1]}
    )
    assert response.status_code == HTTPStatus.OK
    session.expire_all()
    assert not await session.get(User, user_id)


async def test_user_me(
    client, token, session, user_password, lesson, lesson_user, course_term, term_user
):
    user, _ = user_password
    response = client.get(
        "/logged/user/me", auth=token, params={"password": user_password[1]}
    )
    assert response.status_code == HTTPStatus.OK
    result = response.json()
    assert str(user.id) == result["id"]
    assert user.username == result["username"]
    assert user.fullname == result["fullname"]
    assert user.email == result["email"]
    assert len(result["lesson_users"]) == 1
    assert str(lesson.id) == result["lesson_users"][0]["lesson_id"]
    assert str(user.id) == result["lesson_users"][0]["user_id"]
    assert str(lesson.id) == result["lesson_users"][0]["lesson"]["id"]
    assert lesson.title == result["lesson_users"][0]["lesson"]["title"]
    assert len(result["term_users"]) == 1
    assert str(course_term.id) == result["term_users"][0]["term_id"]
    assert str(user.id) == result["term_users"][0]["user_id"]
    assert str(course_term.id) == result["term_users"][0]["term"]["id"]
