from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.models.lab import Container
from app.services.container_service import ContainerService
from app.models.user import User
from app.api.v1.deps import get_current_user,get_current_admin,get_current_teacher_or_admin

router = APIRouter()

@router.post("/start", response_model=Container)
def start_experiment(
    experiment_id: int, # 前端需要传实验ID
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)

):
    """
    启动实验环境
    """
    return ContainerService.get_or_create_container(
        session=session,
        user_id=current_user.id,
        exp_id=experiment_id
    )

@router.post("/stop")
def stop_experiment(
    experiment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    停止实验，释放资源
    """
    return ContainerService.stop_experiment(
        session=session,
        user_id=current_user.id,
        exp_id=experiment_id
    )

@router.post("/reset")
def reset_experiment_environment(
    experiment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    重置实验环境 (仅在未开始实验时可用)
    """
    return ContainerService.reset_workspace(
        session=session,
        user_id=current_user.id,
        exp_id=experiment_id
    )


@router.delete("/admin/stop")
def admin_stop_container(
    experiment_id: int,
    target_user_id: int, # 管理员需要指定删谁的
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_teacher_or_admin) # 必须是管理员
):
    """管理员强制删除某学生的容器"""
    return ContainerService.stop_experiment(session, target_user_id, experiment_id)