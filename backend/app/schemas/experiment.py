from sqlmodel import SQLModel
from app.models.lab import Experiment
from typing import Optional
#继承自数据库模型，但多加一个content字段
class ExperimentDetail(Experiment):
    content: str

class ExperimentId(SQLModel):
    id: Optional[int] = None
