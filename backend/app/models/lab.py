from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    icon: Optional[str] = None
    sort_order: int = Field(default=0)

class Image(SQLModel, table=True):
    __tablename__ = "images"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    docker_tag: str
    default_port: int = 8888
    work_dir: str = "/workspace"

class Experiment(SQLModel, table=True):
    __tablename__ = "experiments"
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id")
    image_id: int = Field(foreign_key="images.id")
    title: str
    description: Optional[str] = None
    doc_path: Optional[str] = None
    template_path: Optional[str] = None
    dataset_path: Optional[str] = None
    image_path: Optional[str] = None
    # --- 新增资源限制字段 ---

    # 1. CPU 限制 (例如: 2.0 表示最多用2个核)
    cpu_limit: float = Field(default=1.0, description="CPU核数限制")

    # 2. 内存限制 (例如: "2g", "512m")
    memory_limit: str = Field(default="1g", description="内存限制")

    # 3. GPU 配置
    use_gpu: bool = Field(default=False, description="是否启用GPU")
    gpu_count: int = Field(default=0, description="GPU数量")

    # 4. (可选) 存储限制 - 防止学生把磁盘写满
    storage_limit: str = Field(default="1g", description="磁盘配额")

class UserLab(SQLModel, table=True):
    __tablename__ = "user_labs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    experiment_id: int = Field(foreign_key="experiments.id")
    status: str = "unstarted"

class Container(SQLModel, table=True):
    __tablename__ = "containers"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    experiment_id: int = Field(foreign_key="experiments.id")
    container_id: str
    host_port: int
    url_token: str
    status: str = "running"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Submission(SQLModel, table=True):
    __tablename__ = "submissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    experiment_id: int = Field(foreign_key="experiments.id")
    student_comment: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[float] = None
    feedback: Optional[str] = None
    grader_id: Optional[int] = Field(default=None, foreign_key="users.id")
    graded_at: Optional[datetime] = None