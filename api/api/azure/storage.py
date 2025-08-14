from datetime import datetime, timedelta
from dateutil.parser import isoparse

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import ContainerClient
from azure.storage.blob import (
    generate_blob_sas,
    BlobSasPermissions,
    BlobServiceClient,
)


from api.settings import (
    ACCOUNT_NAME,
    STORAGE_URL,
    CONTAINER_IMAGE_NAME,
    CONTAINER_SPREADSHEET_NAME,
)

_credential = None
_container_image = None
_container_spreadsheet = None
_delegation_key = None


def get_default_credential():
    global _credential
    if not _credential:
        _credential = DefaultAzureCredential()
    return _credential


def get_container_image():
    global _container_image
    credential = get_default_credential()
    if not _container_image:
        _container_image = ContainerClient(
            STORAGE_URL, CONTAINER_IMAGE_NAME, credential=credential
        )
    return _container_image


def get_container_spreadsheet():
    global _container_spreadsheet
    credential = get_default_credential()
    if not _container_spreadsheet:
        _container_spreadsheet = ContainerClient(
            STORAGE_URL, CONTAINER_SPREADSHEET_NAME, credential=credential
        )
    return _container_spreadsheet


def create_delegation_key(duration_min=10):
    credential = get_default_credential()
    blob_service = BlobServiceClient(STORAGE_URL, credential)
    return blob_service.get_user_delegation_key(
        datetime.now(),
        datetime.now() + timedelta(minutes=duration_min),
    )


def get_delegation_key():
    global _delegation_key
    if not _delegation_key:
        _delegation_key = create_delegation_key()
    else:
        expiry = isoparse(_delegation_key.signed_expiry)
        is_about_to_expiry = expiry < (
            datetime.now(expiry.tzinfo) + timedelta(minutes=1)
        )
        if is_about_to_expiry:
            _delegation_key = create_delegation_key()
    return _delegation_key


def generate_sas(blob_name, duration_min=10):
    delegation_key = get_delegation_key()
    token = generate_blob_sas(
        ACCOUNT_NAME,
        CONTAINER_IMAGE_NAME,
        blob_name,
        user_delegation_key=delegation_key,
        permission=BlobSasPermissions(read=True),
        start=datetime.now(),
        expiry=datetime.now() + timedelta(minutes=duration_min),
    )
    sas = f"{STORAGE_URL}{CONTAINER_IMAGE_NAME}/{blob_name}?{token}"
    return sas
