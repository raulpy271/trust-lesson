from enum import Enum, auto
from datetime import date, time
from pydantic import BaseModel

from pandas import DataFrame


class ParserState(Enum):
    READING_COURSE_NAME = auto()
    READING_TERM_NUMBER = auto()
    READING_LESSONS_COLS = auto()
    READING_LESSONS = auto()


NAME_TAG = "Course name:"
TERM_NUMBER_TAG = "Term number:"
LESSONS_COLS = ["Title", "Date", "Time", "Duration", "Description"]


class LessonItem(BaseModel):
    title: str
    start_date: date
    start_time: time
    duration_min: int
    description: str


class LessonParserResult(BaseModel):
    course_name: str
    term_number: int
    lessons: list[LessonItem]


def parse(df: DataFrame) -> LessonParserResult:
    state = ParserState.READING_COURSE_NAME
    course_name = None
    term_number = None
    lessons = []
    for i, row in df.iterrows():
        if state == ParserState.READING_COURSE_NAME:
            for j, col in enumerate(row.items()):
                if col[1] == NAME_TAG:
                    course_name = row.iloc[j + 1]
                    state = ParserState.READING_TERM_NUMBER
                    break
        elif state == ParserState.READING_TERM_NUMBER:
            for j, col in enumerate(row.items()):
                if col[1] == TERM_NUMBER_TAG:
                    term_number = row.iloc[j + 1]
                    state = ParserState.READING_LESSONS_COLS
                    break
        elif state == ParserState.READING_LESSONS_COLS:
            if LESSONS_COLS == row.to_list():
                state = ParserState.READING_LESSONS
        elif state == ParserState.READING_LESSONS:
            row.index = LessonItem.model_fields.keys()
            lesson = LessonItem(**row.to_dict())
            lessons.append(lesson)
    return LessonParserResult(
        course_name=course_name, term_number=term_number, lessons=lessons
    )
