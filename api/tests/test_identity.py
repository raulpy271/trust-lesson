from http import HTTPStatus
from uuid import uuid4

import mimesis

from api.models import IdentityType


async def test_create(client, token, user_password):
    person = mimesis.Person()
    birth = person.birthdate()
    identity = {
        "user_id": str(user_password[0].id),
        "identity_code": person.identifier(),
        "type": IdentityType.OTHER,
        "fullname": person.full_name(),
        "parent_fullname": person.full_name(),
        "birth_date": str(birth),
        "expiration_date": str(birth),
        "issued_date": str(birth),
        "issuing_authority": "Federal Reserve",
        "country_state": None,
    }
    resp = client.post("logged/user-identity/", json=identity, auth=token)
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert identity["identity_code"] == data["identity_code"]
    assert identity["fullname"] == data["fullname"]
    assert identity["country_state"] == data["country_state"]
    assert identity["user_id"] == data["user_id"]
    assert identity["birth_date"] == data["birth_date"]


async def test_get(client, token, user_password, user_identity):
    resp = client.get(f"logged/user-identity/{user_identity.id}", auth=token)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert user_identity.identity_code == data["identity_code"]
    assert user_identity.fullname == data["fullname"]
    assert user_identity.country_state == data["country_state"]
    assert str(user_identity.user_id) == data["user_id"]
    assert str(user_password[0].id) == data["user_id"]
    assert str(user_identity.birth_date) == data["birth_date"]


async def test_cannot_get_identity_of_another_user(
    client, session, token, user_identity, factory
):
    user_password2 = await factory.user_password(session)
    identity = await factory.user_identity(session, user_password2)
    resp = client.get(f"logged/user-identity/{identity.id}", auth=token)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


async def test_user_doesnt_have_identity(client, token):
    resp = client.get(f"logged/user-identity/{uuid4()}", auth=token)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


async def test_cannot_create_two_identities(
    client, token, user_password, user_identity
):
    person = mimesis.Person()
    birth = person.birthdate()
    identity = {
        "user_id": str(user_password[0].id),
        "identity_code": person.identifier(),
        "type": IdentityType.OTHER,
        "fullname": person.full_name(),
        "parent_fullname": person.full_name(),
        "birth_date": str(birth),
        "expiration_date": str(birth),
        "issued_date": str(birth),
        "issuing_authority": "Federal Reserve",
        "country_state": None,
    }
    resp = client.post("logged/user-identity/", json=identity, auth=token)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


async def test_cannot_update_user_id(
    session, factory, client, token, user_password, user_identity
):
    person = mimesis.Person()
    birth = person.birthdate()
    user_password2 = await factory.user_password(session)
    identity = {
        "user_id": str(user_password2[0].id),
        "identity_code": user_identity.identity_code,
        "type": user_identity.type,
        "fullname": user_identity.fullname,
        "parent_fullname": user_identity.parent_fullname,
        "birth_date": str(birth),
        "expiration_date": str(birth),
        "issued_date": str(birth),
        "issuing_authority": "Federal Reserve",
        "country_state": None,
    }
    resp = client.put(
        f"logged/user-identity/{user_identity.id}", json=identity, auth=token
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
