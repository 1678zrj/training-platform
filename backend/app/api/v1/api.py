from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import categories,experiments
# 假设你也创建了 users.py，即使暂时没内容

api_router = APIRouter()

# 挂载 auth 模块，前缀可以是 /auth
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(categories.router, prefix="/categories",tags=["Categories"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])