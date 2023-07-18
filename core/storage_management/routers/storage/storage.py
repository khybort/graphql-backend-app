import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from core.storage_management.routers.storage.handlers.storage import StorageHandler

router = APIRouter()


@router.get("/storage/{collection}/{id}/{file_name}")
async def storage(collection: str, id: str, file_name: str):
    """
    collection = The values ​​you enter must be comment or application
    """

    handler = StorageHandler.get_handler(collection)
    file_path = handler.get_file_path(id, file_name)
    if not file_path:
        raise HTTPException(status_code=404, detail="Not found")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Not found")

    if (
        collection == "comment"
        or collection == "agents"
        or StorageHandler.validate(file_path)
    ):
        return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="Not found")
