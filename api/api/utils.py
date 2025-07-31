import re
from http import HTTPStatus

from fastapi import UploadFile, HTTPException


def check_media_type(extensions: list[str], mime_types: list[str] = []):
    extensions = [s.lower() for s in extensions]
    mime_types = [s.lower() for s in mime_types]

    def wrapper(file: UploadFile):
        match = re.fullmatch(r"(\w+)/(\w+)", file.content_type.lower())
        if match:
            mime_type, media_type = match.groups()
            if media_type not in extensions:
                raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            if mime_types and mime_type not in mime_types:
                raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            return file
        else:
            raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    return wrapper


def parse_content_type(ct: str) -> tuple[str, str]:
    match = re.fullmatch(r"(\w+)/(\w+)", ct)
    if match:
        return match.groups()
    else:
        raise ValueError("Invalid content type")
