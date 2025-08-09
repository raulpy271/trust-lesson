from enum import Enum, auto
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ValidationError

from pandas import DataFrame, isna


class ParserState(Enum):
    READING_COURSE_NAME = auto()
    READING_TERM_NUMBER = auto()
    READING_LESSONS_COLS = auto()
    READING_LESSONS = auto()


NAME_TAG = "Course name:"
TERM_NUMBER_TAG = "Term number:"
LESSONS_COLS = [
    "Title",
    "Date",
    "Time",
    "Duration",
    "Instructor (optional)",
    "Description",
]


class LessonItem(BaseModel):
    title: str
    start_date: date
    start_time: time
    duration_min: int
    instructor: Optional[str] = None
    description: str


class LessonParserResult(BaseModel):
    course_name: Optional[str]
    term_number: Optional[int]
    lessons: list[LessonItem]
    errors: list[tuple[int, str]] = []
    state_error: Optional[ParserState] = None


def parse(df: DataFrame) -> LessonParserResult:
    state = ParserState.READING_COURSE_NAME
    course_name = None
    term_number = None
    errors = []
    lessons = []
    i = 0
    for i, row in df.iterrows():
        if state == ParserState.READING_COURSE_NAME:
            for j, col in enumerate(row.items()):
                if col[1] == NAME_TAG:
                    if (
                        j + 1 < row.shape[0]
                        and isinstance(row.iloc[j + 1], str)
                        and len(row.iloc[j + 1])
                    ):
                        course_name = row.iloc[j + 1]
                        state = ParserState.READING_TERM_NUMBER
                        break
                    else:
                        errors.append((i, "The name of the course is empty or invalid"))
            if errors:
                break
        elif state == ParserState.READING_TERM_NUMBER:
            for j, col in enumerate(row.items()):
                if col[1] == TERM_NUMBER_TAG:
                    if (
                        j + 1 < row.shape[0]
                        and isinstance(row.iloc[j + 1], int)
                        and row.iloc[j + 1] >= 0
                    ):
                        term_number = row.iloc[j + 1]
                        state = ParserState.READING_LESSONS_COLS
                        break
                    else:
                        errors.append(
                            (i, "The term number of the course is empty or invalid")
                        )
            if errors:
                break
        elif state == ParserState.READING_LESSONS_COLS:
            if LESSONS_COLS == row.to_list():
                state = ParserState.READING_LESSONS
        elif state == ParserState.READING_LESSONS:
            if len(row.index) == len(LessonItem.model_fields.keys()):
                row.index = LessonItem.model_fields.keys()
                try:
                    if isna(row["instructor"]):
                        row["instructor"] = None
                    lesson = LessonItem.model_validate(row.to_dict())
                    lessons.append(lesson)
                except ValidationError as exc:
                    for detail in exc.errors():
                        if detail["loc"][0] == "start_date":
                            errors.append((i, "Invalid format on field start date"))
                        elif detail["loc"][0] == "start_time":
                            errors.append((i, "Invalid format on field start time"))
                        else:
                            errors.append((i, detail["msg"]))
            else:
                errors.append((i, "The format of the spreadsheet is invalid"))
                break
    if not errors and state != ParserState.READING_LESSONS:
        if state == ParserState.READING_COURSE_NAME:
            errors.append((i, "The name of the course was not found"))
        elif state == ParserState.READING_TERM_NUMBER:
            errors.append((i, "The term number of the course was not found"))
        else:
            errors.append((i, "The format of the spreadsheet is invalid"))
    return LessonParserResult(
        course_name=course_name,
        term_number=term_number,
        lessons=lessons,
        errors=errors,
        state_error=state if len(errors) else None,
    )
