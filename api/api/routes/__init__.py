from api.routes import (
    health,
    auth,
    course,
    course_term,
    lesson,
    user,
    identity,
)
from api.routes.validation import lesson as lesson_validation
from api.routes.validation import identity as identity_validation


routes = [
    health.router,
    auth.router,
]


logged = [
    course.router,
    course_term.router,
    lesson.router,
    user.router,
    identity.router,
    lesson_validation.router,
    identity_validation.router,
]
