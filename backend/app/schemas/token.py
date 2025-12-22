from sqlmodel import SQLModel

# 前端登录发过来的 JSON
class UserLogin(SQLModel):
    username: str
    password: str

# 后端返回给前端的 Token
class Token(SQLModel):
    access_token: str
    token_type: str
    role: int
    username: str