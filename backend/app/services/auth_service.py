from sqlmodel import Session
from app.crud import crud_user
from app.core.security import verify_password, create_access_token
from app.models.user import User
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import HTTPException, status


class AuthService:
    @staticmethod
    def authenticate(session: Session, username: str, password: str) -> User | None:
        """
        验证用户身份的核心业务逻辑
        """
        # 1. 查用户
        user = crud_user.get_by_username(session, username)
        print(f"查询到登录用户信息：{user}")
        if not user:
            return None
        # print("开始进行密码验证")
        # 2. 验密码
        if not verify_password(password, user.password_hash):
            return None

        return user


    @staticmethod
    def refresh_token(session: Session, refresh_token: str) -> str:
        """
        验证 refresh_token（包括是否是真的或是否过期）
        如果是真的且未过期，返回新的access_token，
        如果过期了，则报错告知前端退出登录
        """
        try:
            # 1. 解码 token
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            # 2. 校验token类型（防止有人拿access_token 当 refresh_token 用）
            if username is None or token_type != "refresh":
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "无效的刷新令牌"
                )
        except JWTError:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "刷新令牌已过期或无效"
            )
        # 运行到这里说明刷新令牌是有效的
        # 3、 查库确保用户还存在（后续可以添加用户封禁功能：如果用户被封禁，这里能拦住）
        user = crud_user.get_by_username(session, username)
        if user is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "用户不存在"
            )
        # 允许到这里说明用户存在或没被封禁
        # 4、生成新的 Access Token
        new_access_token = create_access_token(data={"sub": user.username, "role": user.role})
        return new_access_token