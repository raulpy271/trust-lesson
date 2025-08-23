import pytest

from api.utils import set_dict_to_tuple


def _compare_tuples(t1, t2):
    assert len(t1) == len(t2)
    if len(t1) > 0:
        if isinstance(t1[0], tuple):
            for i in range(len(t1)):
                assert t1[i][0] == t2[i][0]
                _compare_tuples(t1[i][1], t2[i][1])
        else:
            assert set(t1) == set(t2)


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
            (("hello", ("world", "help")), ("car", (("mobile", ()), ("miss", ())))),
        ),
    ],
)
def test_set_dict_to_tuple(value, expected):
    result = set_dict_to_tuple(value)
    _compare_tuples(result, expected)
