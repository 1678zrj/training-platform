from typing import List
from sqlmodel import Session
from fastapi import HTTPException
from app.crud import crud_experiment
from app.crud import crud_category
from app.models.lab import Experiment


class ExperimentService:
    @staticmethod
    def get_experiments_by_category(session: Session, category_id: int) -> List[Experiment]:
        """
        获取某分类下的实验列表。
        业务逻辑：先检查分类是否存在，不存在则抛错。
        """
        # 1. 检查分类是否存在
        category = crud_category.get_by_id(session, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="该分类不存在")

        # 2. 获取实验
        return crud_experiment.get_by_category(session, category_id)