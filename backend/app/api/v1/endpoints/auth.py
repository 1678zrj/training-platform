from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.token import Token, UserLogin
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, session: Session = Depends(get_session)):
    # 调用 Service 层进行验证

    user = AuthService.authenticate(session, user_in.username, user_in.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    # 运行到这里说明登录验证通过了，该为用户分别生成两种Token了
    # 1、生成 Access Token（短效）
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    # 2、生成 Refresh Token（长效）
    refresh_token = create_refresh_token(data={"sub": user.username, "type": "refresh"})
    # 3、返回双 Token
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "id": user.id
    }


# --- 新增接口: 刷新 Token ---
@router.post("/refresh")
def refresh_token(
        refresh_token: str = Body(..., embed=True),  # 接收前端传来的 { "refresh_token": "..." }
        session: Session = Depends(get_session)
):
    """
    前端拦截器在 Access Token 过期时调用此接口，
    用 Refresh Token 换取新的 Access Token
    """
    new_access_token = AuthService.refresh_token(session, refresh_token)

    # 这里只返回 access_token 即可，refresh_token 通常不需要频繁更换（除非你也做了 Refresh Token 轮换策略）
    return {"access_token": new_access_token}
    # 注意：这里的 key ("accessToken") 要和你前端 request.js 里接收的一致