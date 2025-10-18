from uuid import UUID
from http import HTTPStatus
import logging
import json

import azure.functions as func

from api.jobs import validate_images
from api.jobs import update_status_lesson
from api.health import health
from api.utils import format_traceback
from api.models import AsyncSession, IdentityValidation

from functions.lesson import read_df_from_storage, create_lessons
from functions.lessons_parser import parse
from functions.validator import (
    ValidatorStorage,
    validate_identity,
    create_validation_identity,
)


app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 3 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
async def trigger_update_status_lesson(timer: func.TimerRequest) -> None:
    logging.info("Python timer trigger function running.")
    try:
        await update_status_lesson.run()
        logging.info("Python timer trigger function executed.")
    except Exception as e:
        logging.error(str(e))


@app.timer_trigger(
    schedule="0 3 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
async def trigger_validate_images(timer: func.TimerRequest) -> None:
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
async def upload_spreadsheet(req: func.HttpRequest) -> func.HttpResponse:
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
                result = await create_lessons(parse_result, UUID(data["instructor_id"]))
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
async def functions_health(req: func.HttpRequest) -> func.HttpResponse:
    response, status_code = await health(checks=["database", "storage"])
    body = json.dumps(response.model_dump())
    return func.HttpResponse(
        body=body, status_code=status_code, mimetype="application/json"
    )


@app.route(
    route="validation/user-identity",
    auth_level=func.AuthLevel.FUNCTION,
    methods=[func.HttpMethod.POST],
)
async def validation_user_identity(req: func.HttpRequest) -> func.HttpResponse:
    validate = None
    identity = None
    data = req.get_json()
    if data["filename"] and data["user_id"]:
        try:
            logging.info("processing validation of file" + data["filename"])
            validate = await validate_identity(UUID(data["user_id"]), data["filename"])
            identity = await create_validation_identity(
                validate, UUID(data["user_id"]), data["filename"]
            )
            if identity.validated_success:
                status = HTTPStatus.OK
            else:
                status = HTTPStatus.INTERNAL_SERVER_ERROR
            return func.HttpResponse(
                body=identity.model_dump_json(),
                status_code=status,
                mimetype="application/json",
            )
        except Exception as e:
            logging.error(str(e))
            if not identity:
                async with AsyncSession() as session:
                    identity = IdentityValidation(
                        user_id=data["user_id"],
                        image_path=data["filename"],
                        validated=bool(validate),
                        validated_success=False,
                        error_message=str(e),
                        error_traceback=format_traceback(e),
                    )
                    session.add(identity)
                    await session.commit()
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            return func.HttpResponse(
                body=identity.model_dump_json(),
                status_code=status,
                mimetype="application/json",
            )
    else:
        return func.HttpResponse(
            body=json.dumps({"message": "filename was not set"}),
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json",
        )
