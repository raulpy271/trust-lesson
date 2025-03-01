import mimesis
import pytest

from api import models
from api.auth import create_hash_salt


class Factory:
    def __init__(self):
        self.factories = {}

    def __getattr__(self, name):
        if name in self.factories:
            return self.factories[name]
        else:
            raise ValueError(f"Attribute {name} not found")

    def register(self, func):
        def func_factory(n, *args, **kwargs):
            return [func(*args, **kwargs) for _ in range(n)]

        self.factories["list_" + func.__name__] = func_factory
        self.factories[func.__name__] = func
        return func


factory = Factory()


@pytest.fixture
@factory.register
def user_password(session):
    person = mimesis.Person()
    password = person.password()

    phash, salt = create_hash_salt(password)
    u = models.User(
        username=person.username(),
        fullname=person.full_name(),
        email=person.email(),
        role=models.UserRole.STUDANT,
        password_hash=phash,
        password_salt=salt,
    )
    session.add(u)
    session.commit()
    return (u, password)


@pytest.fixture
@factory.register
def course(session):
    text = mimesis.Text()
    course = models.Course(
        name=text.title(),
        description=text.sentence(),
    )
    session.add(course)
    session.commit()
    return course


@pytest.fixture
@factory.register
def course_term(session, course):
    datetime = mimesis.Datetime()
    term = models.CourseTerm(
        term_number=1,
        status=models.TermStatus.WAITING,
        start_date=datetime.date(),
        end_date=datetime.date(),
        course=course,
    )
    session.add(term)
    session.commit()
    return term


@pytest.fixture
@factory.register
def lesson(session, course_term, user_password, start_date=None):
    user, _ = user_password
    text = mimesis.Text()
    datetime = mimesis.Datetime()
    if not start_date:
        start_date = datetime.datetime()
    lesson = models.Lesson(
        status=models.LessonStatus.WAITING,
        start_date=start_date,
        duration_min=60,
        description=text.sentence(),
        instructor=user,
        term=course_term,
    )
    session.add(lesson)
    session.commit()
    return lesson
