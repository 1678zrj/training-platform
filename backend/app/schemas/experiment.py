from sqlmodel import SQLModel
from app.models.lab import Experiment
from typing import Optional, List
from app.models.lab import ResourceType

#继承自数据库模型，但多加一个content字段
# class ExperimentDetail(Experiment):
#     content: str

class ExperimentId(SQLModel):
    id: Optional[int] = None



class ExperimentResource(SQLModel):
    id: int
    name: str
    resource_type: ResourceType
    file_path_or_url: str
    sort_order: int


class ExperimentDetail(SQLModel):
    id: int
    title: str
    description: Optional[str]

    category_id: int
    image_id: int

    doc_path: Optional[str]
    template_path: Optional[str]
    dataset_path: Optional[str]
    image_path: Optional[str]

    cpu_limit: float
    memory_limit: str
    use_gpu: bool
    gpu_device_ids: Optional[str]
    storage_limit: str

    resources: List[ExperimentResource] = []