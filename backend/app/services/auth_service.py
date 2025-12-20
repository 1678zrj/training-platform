from sqlmodel import Session
from app.crud import crud_user
from app.core.security import verify_password
from app.models.user import User


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
        print("开始进行密码验证")
        # 2. 验密码
        if not verify_password(password, user.password_hash):
            return None

        return user