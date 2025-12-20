from sqlmodel import Session, select
from app.models.user import User
from app.core.security import get_password_hash



def get_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

# def get_by_username(session: Session, username: str):
#     print("DB URL:", session.get_bind().engine.url)
#
#     users = session.exec(select(User)).all()
#     print("All users:", [u.username for u in users])
#
#     statement = select(User).where(User.username == username)
#     result = session.exec(statement).first()
#     print("Query result:", result)
#
#     return result

def create(session: Session, username: str, password: str, role: int = 0) -> User:
    db_user = User(
        username=username,
        password_hash=get_password_hash(password),
        role=role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user