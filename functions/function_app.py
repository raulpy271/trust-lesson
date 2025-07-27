import logging
import json

import azure.functions as func

# from api.jobs import validate_images
from api.jobs import update_status_lesson
from api.health import health

# from functions.validator import ValidatorStorage


app = func.FunctionApp()


@app.timer_trigger(
    schedule="* * * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
def updateStatusLesson(timer: func.TimerRequest) -> None:
    logging.info("Python timer trigger function running.")
    try:
        update_status_lesson.run()
        logging.info("Python timer trigger function executed.")
    except Exception as e:
        logging.error(str(e))


# @app.timer_trigger(
#     schedule="* * * * *", arg_name="timer", run_on_startup=False, use_monitor=False
# )
# async def validateImages(timer: func.TimerRequest) -> None:
#     logging.info("Python timer trigger function running.")
#     try:
#         validator = ValidatorStorage()
#         validate_images.run(validator)
#     except Exception as e:
#         logging.error(str(e))


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
async def functionsHealth(req: func.HttpRequest) -> func.HttpResponse:
    response, status_code = await health(checks=["database", "storage"])
    body = json.dumps(response.model_dump())
    return func.HttpResponse(body=body, status_code=status_code)
