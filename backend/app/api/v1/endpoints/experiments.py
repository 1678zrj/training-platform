from typing import List
from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session
from app.db.session import get_session
from app.models.lab import Experiment
from app.services.experiment_service import ExperimentService
from app.schemas.experiment import ExperimentDetail,ExperimentId

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


@router.get("/{exp_id}", response_model=ExperimentDetail)
def read_experiment_detail(
    exp_id: int = Path(..., description="实验ID"),
    session: Session = Depends(get_session)
):
    """
    获取单个实验的详情（包含Markdown内容）
    """
    return ExperimentService.get_experiment_detail(session, exp_id)

@router.get("/{exp_id}/next", response_model=ExperimentId)
def read_experiment_detail(
    exp_id: int = Path(..., description="当前实验ID"),
    session: Session = Depends(get_session)
):
    """
    获取与当前实验相同分类下的下一个实验的ID
    """
    return ExperimentService.get_next_exp_id(session, exp_id)

@router.get("/{exp_id}/prev", response_model=ExperimentId)
def read_experiment_detail(
    exp_id: int = Path(..., description="当前实验ID"),
    session: Session = Depends(get_session)
):
    """
    获取与当前实验相同分类下的下一个实验的ID
    """
    return ExperimentService.get_prev_exp_id(session, exp_id)