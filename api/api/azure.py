from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import ContainerClient

from api.settings import STORAGE_URL, CONTAINER_IMAGE_NAME

_credential = None
_container_image = None


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
