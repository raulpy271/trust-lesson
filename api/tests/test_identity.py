from http import HTTPStatus

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
