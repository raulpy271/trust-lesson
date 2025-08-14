from api.routes import health, auth, course, course_term


routes = [
    health.router,
    auth.router,
]


logged = [
    course.router,
    course_term.router,
]
