
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select, text

from api import models

def test_db_conn(session):
    result = session.connection().execute(text("select sqlite_version() as v")).all()
    assert len(result) == 1
    assert isinstance(result[0][0], str)

def test_insert(session):
    u1 = models.User(
        username="Raul",
        fullname="Jose Raul",
        email="raul@gmail.com",
        role=models.UserRole.STUDANT,
        password_hash="0000",
        password_salt="0000",
    )
    u2 = models.User(
        username="Maria",
        fullname="Jose Maria",
        email="maria@gmail.com",
        role=models.UserRole.INSTRUCTOR,
        password_hash="0000",
        password_salt="0000",
    )
    session.add_all([u1, u2])
    session.commit()
    us = session.scalars(select(models.User)).all()
    assert len(us) == 2
        
def test_clean_db(session):
    us = session.scalars(select(models.User)).all()
    assert len(us) == 0

def test_uuid_and_default(session):
    c1 = models.Course(
        name="Vi form Scratch",
        description="Learn the Vi text editor from the initial beginning"
    )
    c2 = models.Course(
        name="Emecs form Scratch",
        description="There is nothing to learn about this shit editor",
        terms_count=1,
        terms=[
            models.CourseTerm(
                term_number=1,
                status=models.TermStatus.WAITING,
                start_date=date(year=2024, month=1, day=1),
                end_date=date(year=2024, month=2, day=1)
            )
        ]
    )
    session.add_all([c1, c2])
    session.commit()
    [c1, c2] = session.scalars(select(models.Course)).all()
    assert isinstance(c1.id, UUID)
    assert isinstance(c2.id, UUID)
    assert c1.id != c2.id
    assert c1.terms_count == len(c1.terms) and len(c1.terms) == 0
    assert c2.terms_count == len(c2.terms) and len(c2.terms) == 1
    assert c2.terms[0].course_id == c2.id
    assert c2.terms[0].id != c2.id
    assert c2.terms[0].course == c2

def test_timestemp_column(session):
    before_create = datetime.now()
    m1 = models.Course(
        name="Vi form Scratch",
        description="Learn the Vi text editor from the initial beginning"
    )
    session.add(m1)
    session.commit()
    m2 = models.Course(
        name="Emacs form Scratch",
        description="There is nothing to learn about this shit editor",
    )
    session.add(m2)
    session.commit()
    after_create = datetime.now()
    [c1, c2] = session.scalars(select(models.Course).order_by(models.Course.created_at)).all()
    assert isinstance(c1.updated_at, datetime)
    assert isinstance(c1.created_at, datetime)
    assert isinstance(c2.updated_at, datetime)
    assert isinstance(c2.created_at, datetime)
    assert before_create < c1.created_at and c1.created_at < after_create
    assert before_create < c2.created_at and c2.created_at < after_create
    assert c1.name == m1.name and c2.name == m2.name
    assert c1.created_at < c2.created_at
    assert c1.updated_at < c2.updated_at

def test_update_column(session):
    new_desc = "Learn the best text editor!"
    m = models.Course(
        name="Vi form Scratch",
        description="Learn the Vi text editor from the initial beginning"
    )
    session.add(m)
    session.commit()
    c = session.scalars(select(models.Course)).one()
    before_created_at = c.created_at
    before_updated_at = c.updated_at
    c.description = new_desc
    session.commit()
    c = session.scalars(select(models.Course)).one()
    assert c.description == new_desc
    assert c.created_at == before_created_at
    assert before_updated_at < c.updated_at
    assert c.updated_at < datetime.now()

