import re
from http import HTTPStatus

from fastapi import UploadFile, HTTPException


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


def parse_bearer(token: str) -> str | None:
    match = re.fullmatch(r"Bearer\s+(\w+\.\w+\.\S+)", token)
    if match:
        return match.group(1)


def set_dict_to_tuple(value: set | dict) -> tuple:
    if isinstance(value, set):
        return tuple(value)
    elif isinstance(value, dict):
        values = []
        for k, v in value.items():
            values.append((k, set_dict_to_tuple(v)))
        return tuple(values)
    else:
        raise TypeError(f"Value should be set or dict, got: {type(value)}")
