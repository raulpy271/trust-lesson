import asyncio

from azure.core.exceptions import ResourceExistsError
from api.azure.storage import (
    get_container_image,
    get_container_spreadsheet,
    close_resources,
)


async def main():
    try:
        image = get_container_image()
        try:
            await image.create_container()
            print("Created image container")
        except ResourceExistsError:
            print("Image container already exists")
        spreadsheet = get_container_spreadsheet()
        try:
            await spreadsheet.create_container()
            print("Created spreadsheet container")
        except ResourceExistsError:
            print("Spreadsheet container already exists")
    finally:
        await close_resources()


if __name__ == "__main__":
    asyncio.run(main())
