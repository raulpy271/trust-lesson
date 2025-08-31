import pytest

from api.utils import set_dict_to_tuple


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
