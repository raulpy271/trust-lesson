from sqlalchemy import select, update, event, func

from api import models


@event.listens_for(models.CourseTerm, "before_insert")
def course_term_before_insert(_mapper, connection, course_term):
    stmt = select(func.count(models.CourseTerm.id)).where(
        models.CourseTerm.course_id == course_term.course_id
    )
    count = connection.execute(stmt).scalar_one_or_none() or 0
    connection.execute(stmt)
    course_term.term_number = count


@event.listens_for(models.CourseTerm, "after_insert")
def course_term_after_insert(_mapper, connection, course_term):
    stmt = (
        update(models.Course)
        .where(models.Course.id == course_term.course_id)
        .values(terms_count=course_term.term_number + 1)
    )
    connection.execute(stmt)


@event.listens_for(models.CourseTerm, "after_delete")
def course_term_after_delete(_mapper, connection, course_term):
    stmt = select(func.count(models.CourseTerm.id)).where(
        models.CourseTerm.course_id == course_term.course_id
    )
    count = connection.execute(stmt).scalar_one_or_none() or 0
    stmt = (
        update(models.Course)
        .where(models.Course.id == course_term.course_id)
        .values(terms_count=count)
    )
    connection.execute(stmt)
