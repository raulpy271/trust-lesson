from uuid import UUID
from http import HTTPStatus
import logging
import json

import azure.functions as func

from api.jobs import validate_images
from api.jobs import update_status_lesson
from api.health import health

from functions.lesson import read_df_from_storage, create_lessons
from functions.lessons_parser import parse
from functions.validator import ValidatorStorage


app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 3 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
async def updateStatusLesson(timer: func.TimerRequest) -> None:
    logging.info("Python timer trigger function running.")
    try:
        await update_status_lesson.run()
        logging.info("Python timer trigger function executed.")
    except Exception as e:
        logging.error(str(e))


@app.timer_trigger(
    schedule="0 3 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
async def validateImages(timer: func.TimerRequest) -> None:
    logging.info("Python timer trigger function running.")
    try:
        validator = ValidatorStorage()
        await validate_images.run(validator)
    except Exception as e:
        logging.error(str(e))


@app.route(
    route="lesson/upload-spreadsheet",
    auth_level=func.AuthLevel.FUNCTION,
    methods=[func.HttpMethod.POST],
)
async def uploadSpreadsheet(req: func.HttpRequest) -> func.HttpResponse:
    res = {}
    status = HTTPStatus.OK
    try:
        data = req.get_json()
        if data["filename"] and data["instructor_id"]:
            logging.info("processing upload of file" + data["filename"])
            df = await read_df_from_storage(data["filename"])
            logging.info(f"Shape of the spreadsheet readed {df.shape}")
            parse_result = parse(df)
            if not parse_result.errors:
                logging.info(f"Creating lessons {len(parse_result.lessons)}")
                result = create_lessons(parse_result, UUID(data["instructor_id"]))
                if not result.errors:
                    res = {
                        "course_id": str(result.course_id),
                        "term_id": str(result.term_id),
                    }
                else:
                    status = HTTPStatus.BAD_REQUEST
                    res = {
                        "message": "Error when creating lessons",
                        "errors": result.errors,
                        "state_error": None,
                    }
            else:
                status = HTTPStatus.BAD_REQUEST
                res = {
                    "message": "The spreadsheet sent was some errors",
                    "errors": parse_result.errors,
                    "state_error": parse_result.state_error.value,
                }
        else:
            res = {"message": "filename was not set", "errors": [], "state_error": None}
            status = HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(str(e))
        res = {"message": str(e), "errors": [], "state_error": None}
        status = HTTPStatus.INTERNAL_SERVER_ERROR
    return func.HttpResponse(
        body=json.dumps(res), status_code=status, mimetype="application/json"
    )


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
async def functionsHealth(req: func.HttpRequest) -> func.HttpResponse:
    response, status_code = await health(checks=["database", "storage"])
    body = json.dumps(response.model_dump())
    return func.HttpResponse(
        body=body, status_code=status_code, mimetype="application/json"
    )
