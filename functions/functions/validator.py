import logging
from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

from api.settings import STORAGE_URL
from api.models import LessonValidation
from api.azure.storage import generate_sas
from api.jobs.validate_images import Validator
from functions.settings import VISION_ENDPOINT, VISION_APIKEY


class ValidatorStorage(Validator):
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.blob_service: Optional[BlobServiceClient] = None
        self.client = ImageAnalysisClient(
            endpoint=VISION_ENDPOINT,
            credential=AzureKeyCredential(VISION_APIKEY),
        )
        self.analyze_args = {
            "visual_features": [VisualFeatures.PEOPLE],
            "gender_neutral_caption": False,
        }

    async def __aenter__(self):
        credential = await self.credential.__aenter__()
        self.blob_service = await BlobServiceClient(
            STORAGE_URL, credential
        ).__aenter__()
        await self.client.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.close()
        if self.blob_service:
            await self.blob_service.close()
        await self.credential.close()

    async def get_confidence(self, validation: LessonValidation) -> float:
        confidence = 0
        img_url = await generate_sas(self.blob_service, validation.media_path)
        logging.info(f"Validating image {validation.media_path}")
        result = await self.client.analyze_from_url(img_url, **self.analyze_args)
        logging.info(f"Validation result: {result}")
        persons = result.get("peopleResult", {}).get("values", [])
        if persons:
            confidence = max(map(lambda v: v.get("confidence", 0), persons))
        logging.info(f"Confidence: {confidence}")
        return confidence
