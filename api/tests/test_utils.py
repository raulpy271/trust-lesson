from typing import Optional
import pytest

from api.models import User
from api.utils import set_dict_to_tuple, is_optional_type, to_async


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            {},
            (),
        ),
        (
            {"hello", "world"},
            ("hello", "world"),
        ),
        (
            {"hello": {"world"}},
            (("hello", ("world",)),),
        ),
        (
            {"hello": {"world", "help"}, "car": {"mobile": {}, "miss": {}}},
            (("car", (("miss", ()), ("mobile", ()))), ("hello", ("help", "world"))),
        ),
    ],
)
def test_set_dict_to_tuple(value, expected):
    result = set_dict_to_tuple(value)
    assert result == expected


class _IsOptionalClassTest:
    attr1: int = 0
    attr2: Optional[int] = 2


@pytest.mark.parametrize(
    "cls,arg,expected",
    [
        (_IsOptionalClassTest, "attr1", False),
        (_IsOptionalClassTest, "attr2", True),
        (User, "is_admin", False),
        (User, "validations", False),
        (User, "identity", True),
    ],
)
def test_is_optional_type(cls, arg, expected):
    result = is_optional_type(cls, arg)
    assert result == expected


def test_attr_not_found():
    with pytest.raises(ValueError):
        is_optional_type(_IsOptionalClassTest, "attr5")


async def test_to_async(anyio_backend):
    def f1(x, y):
        return x + y

    def f2(name):
        return "Hello, " + name

    af1 = to_async(f1)
    af2 = to_async(f2)
    assert (await af1(1, 2)) == 3
    assert (await af2("Raul")) == "Hello, Raul"
