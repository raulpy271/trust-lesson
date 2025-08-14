from aiohttp import ClientSession

from api.settings import FUNCTION_URL, FUNCTION_KEY


def function_session():
    headers = {"x-functions-key": FUNCTION_KEY}
    return ClientSession(FUNCTION_URL, headers=headers)
