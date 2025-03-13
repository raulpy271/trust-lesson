from os import environ
import logging

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

from api.models import LessonValidation
from api.azure import generate_sas
from api.jobs import validate_images
from api.jobs import update_status_lesson

VISION_ENDPOINT = environ["VISION_ENDPOINT"]
VISION_APIKEY = environ["VISION_APIKEY"]
app = func.FunctionApp()


class ValidatorStorage(validate_images.Validator):
    def __init__(self):
        self.client = ImageAnalysisClient(
            endpoint=VISION_ENDPOINT, credential=AzureKeyCredential(VISION_APIKEY)
        )
        self.analyze_args = {
            "visual_features": [VisualFeatures.PEOPLE],
            "gender_neutral_caption": False,
        }

    def __call__(self, validation: LessonValidation) -> float:
        confidence = 0
        img_url = generate_sas(validation.media_path)
        logging.info(f"Validating image {validation.media_path}")
        result = self.client.analyze_from_url(img_url, **self.analyze_args)
        logging.info(f"Validation result: {result}")
        persons = result.get("peopleResult", {}).get("values", [])
        if persons:
            confidence = max(map(lambda v: v.get("confidence", 0), persons))
        logging.info(f"Confidence: {confidence}")
        return confidence


@app.timer_trigger(
    schedule="0 3 * * *", arg_name="timer", run_on_startup=False, use_monitor=False
)
def updateStatusLesson(timer: func.TimerRequest) -> None:
    logging.info("Python timer trigger function running.")
    try:
        update_status_lesson.run()
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
        validate_images.run(validator)
    except Exception as e:
        logging.error(str(e))
