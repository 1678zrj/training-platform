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
    # 定义标准认证失败异常（必须是 401，且包含 WWW-Authenticate 头）
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 执行到这里说明jwt解码成功了
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        # 解码成功但是不包含用户名，无法往下校验
        if username is None:
            raise credentials_exception
        # 包含用户名，接下来判断类型，refresh_token不能用来进行校验
        if token_type != "access":
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail= "Token类型错误"
            )

    except JWTError:
        raise credentials_exception
    # 执行到这里就该判断该用户是否存在或是否被禁用了（当前还未添加禁用用户逻辑）
    user = crud_user.get_by_username(session, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 执行到这里说明Token有效且该用户存在
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