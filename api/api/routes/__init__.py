from api.routes import (
    health,
    auth,
    course,
    course_term,
    lesson,
    validation,
    user,
    identity,
)


routes = [
    health.router,
    auth.router,
]


logged = [
    course.router,
    course_term.router,
    lesson.router,
    validation.router,
    user.router,
    identity.router,
]
