from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship


class ResourceType(str, Enum):
    MARKDOWN = "markdown"  # 传统的实验指导书
    PDF = "pdf"            # PDF文档
    VIDEO = "video"        # 视频文件（本地或对象存储）
    LINK = "link"          # 外部链接（如B站视频、Github仓库）
    IMAGE = "image"        # 架构图等辅助图片


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
    work_dir: str = "/home/jovyan/work"

class Experiment(SQLModel, table=True):
    __tablename__ = "experiments"
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id")
    image_id: int = Field(foreign_key="images.id")
    title: str
    description: Optional[str] = None
    doc_path: Optional[str] = None
    template_path: Optional[str] = None
    # 实验的私有数据集或文件路径，和公有的区别开
    dataset_path: Optional[str] = None
    image_path: Optional[str] = None
    # --- 新增资源限制字段 ---

    # 1. CPU 限制 (例如: 2.0 表示最多用2个核)
    cpu_limit: float = Field(default=1.0, description="CPU核数限制")

    # 2. 内存限制 (例如: "2g", "512m")
    memory_limit: str = Field(default="1g", description="内存限制")

    # 3. GPU 配置
    use_gpu: bool = Field(default=False, description="是否启用GPU")
    gpu_device_ids: Optional[str] = Field(default=None, description="指定GPU ID，如 '0' 或 'all',None表示不分配")

    # 4. (可选) 存储限制 - 防止学生把磁盘写满
    storage_limit: str = Field(default="1g", description="磁盘配额")

    # 【ORM 关系】方便代码中直接通过 experiment.resources 获取列表
    resources: List["ExperimentResource"] = Relationship(back_populates="experiment")


# --- 新增：实验资源表 (解决多文件/视频问题) ---
class ExperimentResource(SQLModel, table=True):
    __tablename__ = "experiment_resources"

    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: int = Field(foreign_key="experiments.id", index=True)

    name: str = Field(description="资源显示的名称，如：第一章：环境配置视频")
    resource_type: ResourceType = Field(description="资源类型：pdf, video, markdown等")

    # 这里存储具体的路径或URL
    # 如果是 video，可能是 http://oss.../1.mp4 或 bilibili iframe code
    # 如果是 markdown，可能是 /data/docs/exp1/intro.md
    file_path_or_url: str

    # 排序字段，保证前端展示的顺序（先看文档，再看视频等）
    sort_order: int = Field(default=0, description="展示顺序，越小越靠前")

    experiment: Optional[Experiment] = Relationship(back_populates="resources")

class UserLab(SQLModel, table=True):
    __tablename__ = "user_labs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    experiment_id: int = Field(foreign_key="experiments.id")
    status: str = "unstarted"

class Container(SQLModel, table=True):
    __tablename__ = "containers"
    # 添加联合唯一约束：同一个 user_id 和 experiment_id 只能有一条记录
    __table_args__ = (
        UniqueConstraint("user_id", "experiment_id", name="unique_user_experiment_container"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    experiment_id: int = Field(foreign_key="experiments.id")
    # 容器信息（允许为空，因为占位时还不知道这些）
    container_id: Optional[str] = None
    host_port: Optional[int] = None
    url_token: Optional[str] = None
    base_url: Optional[str] = None

    # 状态增加一种：creating
    status: str = Field(default="creating")
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