from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.models.lab import Container
from app.services.container_service import ContainerService

router = APIRouter()

@router.post("/start", response_model=Container)
def start_experiment(
    experiment_id: int, # 前端需要传实验ID
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    启动实验环境
    """
    return ContainerService.get_or_create_container(
        session=session,
        user_id=user_id,
        exp_id=experiment_id
    )

@router.post("/stop")
def stop_experiment(
    experiment_id: int,
    user_id: int,
    session: Session = Depends(get_session)
):
    """
    停止实验，释放资源
    """
    return ContainerService.stop_experiment(
        session=session,
        user_id=user_id,
        exp_id=experiment_id
    )