import re
from http import HTTPStatus

from aiohttp import ClientSession
from fastapi import UploadFile, HTTPException

from api.settings import FUNCTION_URL, FUNCTION_KEY


def check_media_type(
    extensions: list[str], media_types: list[str] = [], mime_types: list[str] = []
):
    extensions = [s.lower() for s in extensions]
    media_types = [s.lower() for s in media_types]
    mime_types = [s.lower() for s in mime_types]

    def wrapper(file: UploadFile):
        if extensions:
            match = re.fullmatch(r".*\.(\w+)$", file.filename.lower())
            if match:
                ext = match.group(1)
                if ext not in extensions:
                    raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            else:
                raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        if media_types or mime_types:
            match = re.fullmatch(r"(\w+)/(\w+)", file.content_type.lower())
            if match:
                mime_type, media_type = match.groups()
                if media_types and media_type not in media_types:
                    raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
                if mime_types and mime_type not in mime_types:
                    raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            else:
                raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        return file

    return wrapper


def parse_content_type(ct: str) -> tuple[str, str]:
    match = re.fullmatch(r"(\w+)/(\w+)", ct)
    if match:
        return match.groups()
    else:
        raise ValueError("Invalid content type")


def function_session():
    headers = {"x-functions-key": FUNCTION_KEY}
    return ClientSession(FUNCTION_URL, headers=headers)
