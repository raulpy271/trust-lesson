import logging

from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

from api.models import LessonValidation
from api.azure.storage import generate_sas
from api.jobs.validate_images import Validator
from functions.settings import VISION_ENDPOINT, VISION_APIKEY


class ValidatorStorage(Validator):
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
