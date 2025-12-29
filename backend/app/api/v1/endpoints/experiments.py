from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.db.session import get_session
from app.models.lab import Experiment
from app.services.experiment_service import ExperimentService

router = APIRouter()

@router.get("/", response_model=List[Experiment])
def read_experiments(
    category_id: int = Query(..., description="分类ID"),
    session: Session = Depends(get_session)
):
    """
    根据分类ID获取实验列表
    URL示例: /api/v1/experiments/?category_id=1
    """
    return ExperimentService.get_experiments_by_category(session, category_id)