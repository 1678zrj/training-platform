import os
from typing import List
from sqlmodel import Session
from fastapi import HTTPException
from app.crud import crud_experiment
from app.crud import crud_category
from app.models.lab import Experiment
from app.schemas.experiment import ExperimentId,ExperimentDetail

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

    @staticmethod
    def get_experiment_detail(session: Session, exp_id: int) -> Experiment:
        """
        获取实验详情 + 读取 Markdown 文件内容
        """
        # 1. 查数据库
        exp = crud_experiment.get_by_id(session, exp_id)
        if not exp:
            raise HTTPException(status_code=404, detail="实验不存在")
        return exp

        # 2. 读取文件逻辑
        # 假设你的文件都在项目根目录下的 data/ 文件夹里
        # 实际路径 = 项目根目录 + /data + /docs/exp1.md
        # base_path = os.getcwd()  # 或者你指定的绝对路径
        # file_path = os.path.join(base_path, "media", exp.doc_path.lstrip("/"))
        #
        # content = ""
        # try:
        #     if os.path.exists(file_path):
        #         with open(file_path, 'r', encoding='utf-8') as f:
        #             content = f.read()
        #     else:
        #         content = f"# 错误\n\n找不到文件: {file_path}，请联系管理员上传文档。"
        # except Exception as e:
        #     content = f"# 读取错误\n\n{str(e)}"
        #
        # # 3. 构造返回数据 (将对象转字典并追加 content)
        # exp_dict = exp.model_dump()
        # exp_dict['content'] = content
        # return exp_dict

    @staticmethod
    def get_next_exp_id(session: Session, exp_id: int) -> ExperimentId:
        current_exp = crud_experiment.get_by_id(session,exp_id)
        next_exp = crud_experiment.get_next_exp(session,exp_id,current_exp.category_id)
        if not next_exp:
            return ExperimentId()
        return ExperimentId(id=next_exp.id)

    @staticmethod
    def get_prev_exp_id(session: Session, exp_id: int) -> ExperimentId:
        current_exp = crud_experiment.get_by_id(session,exp_id)
        prev_exp = crud_experiment.get_prev_exp(session,exp_id,current_exp.category_id)
        if not prev_exp:
            return ExperimentId()
        return ExperimentId(id=prev_exp.id)

