import logging
from typing import Optional
from uuid import UUID

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    AnalyzeResult,
    DocumentAnalysisFeature,
)

from api.settings import STORAGE_URL
from api.azure.storage import generate_sas
from api.jobs.validate_images import Validator
from api.models import (
    AsyncSession,
    LessonValidation,
    IdentityValidation,
    IdentityType,
)
from functions.settings import (
    VISION_ENDPOINT,
    VISION_APIKEY,
    DOCUMENT_INTELLIGENCE_ENDPOINT,
    DOCUMENT_INTELLIGENCE_APIKEY,
    DOCUMENT_INTELLIGENCE_LOCALE,
)


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


async def validate_identity(user_id: UUID, filename: str) -> AnalyzeResult:
    async with (
        DefaultAzureCredential() as credential,
        BlobServiceClient(STORAGE_URL, credential) as blob_service,
    ):
        img_url = await generate_sas(blob_service, filename)
        di_args = {
            "endpoint": DOCUMENT_INTELLIGENCE_ENDPOINT,
            "credential": AzureKeyCredential(DOCUMENT_INTELLIGENCE_APIKEY),
        }
        async with DocumentIntelligenceClient(**di_args) as client:
            request = AnalyzeDocumentRequest(url_source=img_url)
            poller = await client.begin_analyze_document(
                "prebuilt-idDocument",
                request,
                locale=DOCUMENT_INTELLIGENCE_LOCALE,
                query_fields=["Fullname", "MotherFullname", "FatherFullname"],
                features=[DocumentAnalysisFeature.QUERY_FIELDS],
            )
            result = await poller.result()
            if result.warnings:
                exc_msg = "There are some warnings in the document"
                for warn in result.warnings:
                    exc_msg += ". " + warn.message
                    logging.info(f"Warning: {warn.as_dict()}")
                raise Exception(exc_msg)
            if not result.documents:
                raise Exception("There are not documents to validate.")
            return result


async def create_validation_identity(
    validation_res: AnalyzeResult, user_id: UUID, filename: str
) -> IdentityValidation:
    fields_mapping = {
        "Fullname": "fullname",
        "DocumentNumber": "identity_code",
        "DateOfBirth": "birth_date",
        "DateOfExpiration": "expiration_date",
        "DateOfIssue": "issued_date",
        "IssuingAuthority": "issuing_authority",
        "Region": "country_state",
    }
    doctypes = {
        "idDocument.nationalIdentityCard": IdentityType.IDENTITY_CARD,
        "idDocument.driverLicense": IdentityType.DRIVER_LICENSE,
        "idDocument.passport": IdentityType.PASSPORT,
    }
    validation_args = {}
    for document in validation_res.documents:
        logging.info(document.doc_type)
        logging.info(str(document.fields))
        validation_args["type"] = doctypes.get(document.doc_type, None)
        validation_args["type_confidence"] = document.confidence
        for field_key, field in document.fields.items():
            if field_key in fields_mapping and field.get("content"):
                if field["type"] == "string":
                    validation_args[fields_mapping[field_key]] = field["valueString"]
                elif field["type"] == "date":
                    validation_args[fields_mapping[field_key]] = field["valueDate"]
                validation_args[fields_mapping[field_key] + "_confidence"] = field[
                    "confidence"
                ]
        if "MotherFullname" in document.fields and document.fields[
            "MotherFullname"
        ].get("valueString"):
            validation_args["parent_fullname"] = document.fields["MotherFullname"][
                "valueString"
            ]
            validation_args["parent_fullname_confidence"] = document.fields[
                "MotherFullname"
            ]["confidence"]
        elif "FatherFullname" in document.fields and document.fields[
            "FatherFullname"
        ].get("valueString"):
            validation_args["parent_fullname"] = document.fields["FatherFullname"][
                "valueString"
            ]
            validation_args["parent_fullname_confidence"] = document.fields[
                "FatherFullname"
            ]["confidence"]
    logging.info(str(validation_args))
    async with AsyncSession() as session:
        validation_args["user_id"] = user_id
        validation_args["image_path"] = filename
        validation_args["validated"] = True
        validation_args["validated_success"] = True
        validation = IdentityValidation(**validation_args)
        session.add(validation)
        await session.commit()
    return validation
