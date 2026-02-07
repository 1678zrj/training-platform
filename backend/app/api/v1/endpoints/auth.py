from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Cookie
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.token import Token, UserLogin
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
        response: Response, # 需要用到 Response 对象来设置 Cookie,
        user_in: UserLogin,
        session: Session = Depends(get_session)
):
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
    # 2. 【关键修改】将 Refresh Token 写入 HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # 禁止 JS 读取，防 XSS
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",  # 防 CSRF
        secure=False,  # 开发环境 False (HTTP)，生产环境必须 True (HTTPS)
    )

    # 3、返回 Token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "id": user.id
    }


# --- 新增接口: 刷新 Token ---
@router.post("/refresh")
def refresh_token(
        response: Response,
        refresh_token: str | None = Cookie(default=None),  # 从Cookie中读取refresh_token，而不是Body
        session: Session = Depends(get_session)
):
    """
    前端拦截器在 Access Token 过期时调用此接口，
    用 Refresh Token 换取新的 Access Token
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="未提供刷新令牌")
    new_access_token = AuthService.refresh_token(session, refresh_token)

    # 这里只返回 access_token 即可，refresh_token 通常不需要频繁更换（除非你也做了 Refresh Token 轮换策略）
    return {"access_token": new_access_token}
    # 注意：这里的 key ("access_token") 要和你前端 request.js 里接收的一致

@router.post("/logout")
def logout(response:Response):
    response.delete_cookie("refresh_token")
    return {"message": "登出成功"}
