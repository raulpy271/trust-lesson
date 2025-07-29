from datetime import date, time
from functions.lessons_parser import parse
import pandas
import pytest


@pytest.mark.parametrize(
    "df,expected",
    [
        (
            pandas.read_excel("tests/mock/lessons1.xlsx"),
            {
                "course_name": "name…",
                "term_number": 1,
                "lessons": [
                    {
                        "title": "First Lesson",
                        "start_date": date(day=10, month=12, year=2025),
                        "start_time": time(hour=10, minute=0, second=0),
                        "duration_min": 60,
                        "description": "description of the first lesson",
                    }
                ],
            },
        ),
        (
            pandas.read_excel("tests/mock/lessons2.xlsx"),
            {
                "course_name": "Learn Python",
                "term_number": 2,
                "lessons": [
                    {
                        "title": "Python Basics 1",
                        "start_date": date(day=10, month=12, year=2025),
                        "start_time": time(hour=10, minute=0, second=0),
                        "duration_min": 60,
                        "description": "Lesson about variables and basic math",
                    },
                    {
                        "title": "Python Basics 2",
                        "start_date": date(day=11, month=12, year=2025),
                        "start_time": time(hour=12, minute=0, second=0),
                        "duration_min": 60,
                        "description": "Conditional and loop statements",
                    },
                ],
            },
        ),
    ],
)
def test_parser(df, expected):
    result = parse(df)
    assert result.course_name == expected["course_name"]
    assert result.term_number == expected["term_number"]
    assert len(result.lessons) == len(expected["lessons"])
    for i in range(len(result.lessons)):
        assert result.lessons[i].title == expected["lessons"][i]["title"]
        assert result.lessons[i].start_date == expected["lessons"][i]["start_date"]
        assert result.lessons[i].start_time == expected["lessons"][i]["start_time"]
        assert result.lessons[i].duration_min == expected["lessons"][i]["duration_min"]
        assert result.lessons[i].description == expected["lessons"][i]["description"]
