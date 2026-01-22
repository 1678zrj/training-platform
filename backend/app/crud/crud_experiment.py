from typing import List, Optional
from sqlmodel import Session, select
from app.models.lab import Experiment
from sqlalchemy.orm import selectinload
def get_by_category(session: Session, category_id: int) -> List[Experiment]:
    # 查询指定分类下的所有实验
    statement = select(Experiment).where(Experiment.category_id == category_id)
    return session.exec(statement).all()

def get_by_id(session: Session, exp_id: int) -> Experiment | None:
    """
            根据ID获取实验，并预加载资源列表
            """
    statement = (
        select(Experiment)
        .where(Experiment.id == exp_id)
        # 关键：使用 selectinload 预先抓取 resources 关系
        .options(selectinload(Experiment.resources))
    )
    result = session.exec(statement).first()
    return result

def get_next_exp(session: Session, exp_id: int, category_id: int) -> Experiment |None:
    stmt = select(Experiment).where(
        Experiment.category_id == category_id,
        Experiment.id > exp_id
    ).order_by(
        Experiment.id.asc()
    ).limit(1)
    next_exp = session.exec(stmt).first()
    return next_exp

def get_prev_exp(session: Session, exp_id: int, category_id: int) -> Experiment |None:
    stmt = select(Experiment).where(
        Experiment.category_id == category_id,
        Experiment.id < exp_id
    ).order_by(
        Experiment.id.desc()
    ).limit(1)
    next_exp = session.exec(stmt).first()
    return next_exp