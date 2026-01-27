import os.path
from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session
from app.db.session import get_session
from app.models.lab import ExperimentResource
from app.services.experiment_resource_service import ExperimentResourceService
from fastapi import HTTPException
router = APIRouter()


@router.get("/{resource_id}/content")
def get_resource_content(
        resource_id: int,
        session: Session = Depends(get_session)
):
    try:
        content = ExperimentResourceService.get_file_content(resource_id,session)
        return content
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )