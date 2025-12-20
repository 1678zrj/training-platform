from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db.session import engine, Session
from app.core.config import settings
from app.api.v1.api import api_router
from app.crud import crud_user
# 必须显式导入模型，否则 create_all 无法建表
from app.models.user import User
from app.models.lab import Category,Image,Experiment,UserLab,Container,Submission

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 自动建表
    SQLModel.metadata.create_all(engine)

    # 2. 初始化管理员
    with Session(engine) as session:
        if not crud_user.get_by_username(session, "admin"):
            print("--- 初始化: 创建默认管理员 admin / 123456 ---")
            crud_user.create(session, "admin", "123456", role=2)

    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 挂载 API V1 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "System Running"}