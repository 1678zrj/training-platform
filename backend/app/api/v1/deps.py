from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.crud import crud_user

# 定义 Token 获取方式 (从 Header: Authorization: Bearer <token> 取)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 1. 基础依赖：获取当前登录用户 (验证 Token 有效性)
def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    # --- 新增调试代码 ---
    print(f"DEBUG: 当前使用的 Secret Key 开头: {settings.SECRET_KEY[:5]}")
    print(f"DEBUG: 当前连接的数据库: {settings.DATABASE_URL}")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token 无效")
    except JWTError:
        raise HTTPException(status_code=403, detail="Token 解析失败")
    
    user = crud_user.get_by_username(session, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

# 2. 进阶依赖：必须是管理员 (Role = 2)
def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != 2:
        raise HTTPException(status_code=403, detail="权限不足：需要管理员权限")
    return current_user

# 3. 进阶依赖：必须是老师或管理员 (Role >= 1)
def get_current_teacher_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role < 1:
        raise HTTPException(status_code=403, detail="权限不足：需要教师权限")
    return current_user