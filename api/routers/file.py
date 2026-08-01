from fastapi import APIRouter
from api.models import (
    FolderOpenRequest, FolderCreateRequest, FileCopyMoveRequest,
    FileRenameRequest, FileSearchRequest, FileDeleteRequest, APIResponse
)
from system.file_explorer import file_explorer

router = APIRouter(prefix="/file", tags=["File Explorer"])

@router.post("/open_folder", response_model=APIResponse)
def open_folder(req: FolderOpenRequest):
    """Opens folder or lists directory contents."""
    res = file_explorer.open_folder(req.folder_path)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/create_folder", response_model=APIResponse)
def create_folder(req: FolderCreateRequest):
    """Creates directory path."""
    res = file_explorer.create_folder(req.path)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/copy", response_model=APIResponse)
def copy_item(req: FileCopyMoveRequest):
    """Copies file or folder."""
    res = file_explorer.copy_item(req.src, req.dst)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/move", response_model=APIResponse)
def move_item(req: FileCopyMoveRequest):
    """Moves file or folder."""
    res = file_explorer.move_item(req.src, req.dst)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/rename", response_model=APIResponse)
def rename_item(req: FileRenameRequest):
    """Renames file or folder."""
    res = file_explorer.rename_item(req.src, req.new_name)
    return APIResponse(status=res.get("status", "success"), data=res)

@router.post("/search", response_model=APIResponse)
def search_files(req: FileSearchRequest):
    """Searches files by glob pattern under root directory."""
    res = file_explorer.search_files(req.root_dir, req.pattern)
    return APIResponse(status="success", data={"matches_count": len(res), "files": res})

@router.post("/delete", response_model=APIResponse)
def delete_item(req: FileDeleteRequest):
    """
    Deletes file or folder.
    REQUIRES CONFIRMATION: `confirmed: true`.
    """
    res = file_explorer.delete_item(req.target_path, confirmed=req.confirmed)
    return APIResponse(status=res.get("status", "success"), data=res)
