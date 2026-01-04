from sqlmodel import SQLModel
from app.models.lab import Experiment

#继承自数据库模型，但多加一个content字段
class ExperimentDetail(Experiment):
    content: str
