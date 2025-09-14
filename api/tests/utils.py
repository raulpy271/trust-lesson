import httpx
import inspect
import asyncio


def authenticate(client, user, password):
    resp = client.post("auth/login", json={"email": user.email, "password": password})
    assert resp.headers.get("Token")
    return BearerAuth(resp.headers["Token"])


class BearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token
        self.authorization = f"Bearer {self.token}"

    def auth_flow(self, request):
        request.headers["Authorization"] = self.authorization
        yield request


def is_async(f):
    return inspect.isasyncgenfunction(f) or asyncio.iscoroutinefunction(f)
