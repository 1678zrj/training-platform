from typing import List, Optional
from sqlmodel import Session, select
from app.models.lab import Experiment

def get_by_category(session: Session, category_id: int) -> List[Experiment]:
    # 查询指定分类下的所有实验
    statement = select(Experiment).where(Experiment.category_id == category_id)
    return session.exec(statement).all()

def get_by_id(session: Session, exp_id: int) -> Experiment | None:
    return session.get(Experiment, exp_id)

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