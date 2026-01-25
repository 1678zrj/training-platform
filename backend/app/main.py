from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, select
from fastapi.staticfiles import StaticFiles

from app.db.session import engine, Session
from app.core.config import settings
from app.api.v1.api import api_router
from app.crud import crud_user
# 必须显式导入模型，否则 create_all 无法建表
from app.models.user import User
from app.models.lab import Category,Image,Experiment,UserLab,Container,Submission,ExperimentResource,ResourceType

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 自动建表
    SQLModel.metadata.create_all(engine)

    # 2. 初始化管理员
    with Session(engine) as session:
        if not crud_user.get_by_username(session, "admin"):
            print("--- 初始化: 创建默认管理员 admin / 123456 ---")
            crud_user.create(session, "admin", "123456", role=2)
            crud_user.create(session, "zs", "123456", role=0)
            crud_user.create(session, "ls", "123456", role=0)
            crud_user.create(session, "zj1", "123456", role=1)
        # 2. [新增] 初始化分类数据 (如果表是空的)
        if not session.exec(select(Category)).first():
            print("--- 初始化: 写入测试分类与实验数据 ---")

            # 创建镜像 (Mock)
            img = Image(name="base-notebook", docker_tag="lab-images/base-notebook:latest")
            img2 = Image(name="scipy-notebook", docker_tag="lab-images/scipy-notebook:latest")
            session.add(img)
            session.add(img2)
            session.commit()
            session.refresh(img)

            # 创建分类
            cat1 = Category(name="人工智能原理", code="ai-principle", icon="", sort_order=0)
            cat2 = Category(name="通识课程", code="ai-common", icon="", sort_order=0)
            session.add(cat1)
            session.add(cat2)
            session.commit()
            session.refresh(cat1)
            session.refresh(cat2)
            # 创建实验
            exp1 = Experiment(
                category_id=cat1.id,
                image_id=img.id,
                title="吃豆人-DQN",
                doc_path="/docs/pacman.md",
                template_path="/exp1",
                image_path="/images/Packman.png",
                description="基于强化学习算法实现吃豆人游戏的训练与控制"
            )
            exp2 = Experiment(
                category_id=cat1.id,
                image_id=img2.id,
                title="大语言模型水印检测",
                doc_path="/docs/watermark.md",
                template_path="/exp2",
                image_path="/images/Watermark.png",
                description="实现大模型文本水印嵌入与效果测试",
                use_gpu=True,
                gpu_device_ids="0"

            )
            session.add(exp1)
            session.add(exp2)
            session.commit()
            session.refresh(exp1)
            session.refresh(exp2)
            # 创建实验资源表
            resource1 = ExperimentResource(
                experiment_id = exp1.id,
                name = "实验说明",
                resource_type = ResourceType.MARKDOWN,
                file_path_or_url = "/docs/pacman.md",
            )
            resource2 = ExperimentResource(
                experiment_id=exp2.id,
                name="实验说明",
                resource_type=ResourceType.MARKDOWN,
                file_path_or_url="/docs/watermark.md",
            )
            resource3 = ExperimentResource(
                experiment_id=exp2.id,
                name="实验说明2",
                resource_type=ResourceType.MARKDOWN,
                file_path_or_url="/docs/watermark.md",
            )
            session.add(resource1)
            session.add(resource2)
            session.add(resource3)
            session.commit()
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)


# =========================
# 文件资源挂载
# =========================
# 不再用后端挂载文件资源，这对后端消耗过大
# app.mount(
#     "/media",
#     StaticFiles(directory="media"),
#     name="media"
# )

# 挂载 API V1 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "System Running"}