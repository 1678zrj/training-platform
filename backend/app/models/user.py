from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"

    # 【关键修改】将 Field(primary_key=True) 作为默认值赋值
    # 这样 SQLAlchemy 才能 100% 识别这是主键
    id: int | None = Field(default=None, primary_key=True)

    # 推荐：其他涉及数据库约束（unique, index）的字段也建议改用这种写法
    username: str = Field(unique=True, index=True)

    password_hash: str

    # role 字段同样建议修改，以确保 description 和默认值被正确处理
    role: int = Field(default=0, description="0=学生, 1=老师, 2=管理员")