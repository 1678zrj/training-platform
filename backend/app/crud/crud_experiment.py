from typing import List, Optional
from sqlmodel import Session, select
from app.models.lab import Experiment

def get_by_category(session: Session, category_id: int) -> List[Experiment]:
    # 查询指定分类下的所有实验
    statement = select(Experiment).where(Experiment.category_id == category_id)
    return session.exec(statement).all()

def get_by_id(session: Session, exp_id: int) -> Experiment | None:
    return session.get(Experiment, exp_id)