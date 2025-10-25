import re
import asyncio
import inspect
from types import UnionType
from traceback import format_tb
from typing import Union, get_origin, get_args
from http import HTTPStatus

from sqlalchemy.orm import Mapped
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
        return tuple(sorted(value))
    elif isinstance(value, dict):
        values = []
        for k, v in sorted(value.items(), key=lambda kv: kv[0]):
            values.append((k, set_dict_to_tuple(v)))
        return tuple(values)
    else:
        raise TypeError(f"Value should be set or dict, got: {type(value)}")


def is_optional_type(cls, attr):
    hints = cls.__annotations__
    type_hint = hints.get(attr, None)
    if type_hint:
        origin = get_origin(type_hint)
        args = get_args(type_hint)
        if origin is Mapped:
            origin = get_origin(args[0])
            args = get_args(args[0])
        if (origin is Union or origin == UnionType) and type(None) in args:
            return True
        return False
    else:
        raise ValueError(f"There is no type hint for the attribute {attr}")


def is_async(f):
    return inspect.isasyncgenfunction(f) or asyncio.iscoroutinefunction(f)


def to_async(f):
    async def asyncf(*args, **kwargs):
        return f(*args, **kwargs)

    return asyncf


def format_traceback(e: BaseException) -> str:
    tb = format_tb(e.__traceback__)
    return "\n".join(tb)


def remove_mask(s: str) -> str:
    mask_chars_re = re.compile(r"[.\/\-]")
    return mask_chars_re.sub("", s)


def compare_code(c1: str, c2: str) -> bool:
    return int(remove_mask(c1)) == int(remove_mask(c2))
