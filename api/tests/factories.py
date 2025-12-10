from api.models.user import IdentityType, UserRole
import mimesis
import pytest

from api import models
from api.auth import create_hash_salt
from api.utils import is_async


class Factory:
    def __init__(self):
        self.factories = {}

    def __getattr__(self, name):
        if name in self.factories:
            return self.factories[name]
        else:
            raise ValueError(f"Attribute {name} not found")

    def register(self, func):
        if is_async(func):

            async def func_factory(n, *args, **kwargs):
                return [await func(*args, **kwargs) for _ in range(n)]

        else:

            def func_factory(n, *args, **kwargs):
                return [func(*args, **kwargs) for _ in range(n)]

        self.factories["list_" + func.__name__] = func_factory
        self.factories[func.__name__] = func
        return func


_factory = Factory()


@pytest.fixture
def factory():
    return _factory


@pytest.fixture
@_factory.register
async def user_password(session):
    person = mimesis.Person()
    password = person.password(length=10) + "Ra$0"

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
    await session.commit()
    return (u, password)


@pytest.fixture
@_factory.register
async def admin(user_password, session):
    user, _ = user_password
    user.is_admin = True
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
@_factory.register
async def course(session):
    text = mimesis.Text()
    course = models.Course(
        name=text.title(),
        description=text.sentence(),
    )
    session.add(course)
    await session.commit()
    return course


@pytest.fixture
@_factory.register
async def course_term(session, course):
    datetime = mimesis.Datetime()
    term = models.CourseTerm(
        term_number=1,
        status=models.TermStatus.WAITING,
        start_date=datetime.date(),
        end_date=datetime.date(),
        course=course,
    )
    session.add(term)
    await session.commit()
    return term


@pytest.fixture
@_factory.register
async def term_user(session, course_term, user_password, role=UserRole.STUDANT):
    tu = models.TermUser(
        term_id=course_term.id,
        user_id=user_password[0].id,
        role=role,
    )
    session.add(tu)
    await session.commit()
    return tu


@pytest.fixture
@_factory.register
async def lesson(session, course_term, user_password, start_date=None):
    user, _ = user_password
    text = mimesis.Text()
    datetime = mimesis.Datetime()
    if not start_date:
        start_date = datetime.datetime()
    lesson = models.Lesson(
        title=text.title(),
        status=models.LessonStatus.WAITING,
        start_date=start_date,
        duration_min=60,
        description=text.sentence(),
        instructor=user,
        term=course_term,
    )
    session.add(lesson)
    await session.commit()
    return lesson


@pytest.fixture
@_factory.register
async def lesson_user(
    session, user_password, lesson, validated=False, validated_success=False
):
    user, _ = user_password
    lesson_user = models.LessonUser(
        user_id=user.id,
        lesson_id=lesson.id,
        validated=validated,
        validated_success=validated_success,
    )
    session.add(lesson_user)
    await session.commit()
    return lesson_user


@pytest.fixture
@_factory.register
async def lesson_validation(
    session,
    user_password,
    lesson,
    lesson_user,
    validated=False,
    validated_success=False,
):
    user, _ = user_password
    validation = models.LessonValidation(
        validated=validated,
        validated_success=validated_success,
        media_path="image.jpg",
        media_type=models.MediaType.IMAGE,
        lesson=lesson,
        user=user,
        lesson_user=lesson_user,
    )
    session.add(validation)
    await session.commit()
    return validation


@pytest.fixture
@_factory.register
async def identity_validation(
    session,
    user_password,
    validated=False,
    validated_success=False,
):
    user, _ = user_password
    person = mimesis.Person()
    rand = mimesis.random.Random()

    def conf():
        mimesis.Numeric().float_number(0, 1)

    validation = models.IdentityValidation(
        validated=validated,
        validated_success=validated_success,
        image_path="image.jpg",
        user=user,
        identity_code=person.identifier(),
        identity_code_confidence=conf(),
        type=rand.choice_enum_item(IdentityType),
        type_confidence=conf(),
        fullname=person.full_name(),
        fullname_confidence=conf(),
        parent_fullname=person.full_name(),
        parent_fullname_confidence=conf(),
        birth_date=person.birthdate(),
        birth_date_confidence=conf(),
    )
    session.add(validation)
    await session.commit()
    return validation


@pytest.fixture
@_factory.register
async def user_identity(session, user_password):
    user, _ = user_password
    person = mimesis.Person()
    rand = mimesis.random.Random()
    ui = models.UserIdentity(
        identity_code=person.identifier(),
        type=rand.choice_enum_item(IdentityType),
        fullname=person.full_name(),
        parent_fullname=person.full_name(),
        birth_date=person.birthdate(),
        expiration_date=person.birthdate(),
        issued_date=person.birthdate(),
        issuing_authority="Federal Reserve",
        country_state=None,
        user=user,
    )
    session.add(ui)
    await session.commit()
    return ui
