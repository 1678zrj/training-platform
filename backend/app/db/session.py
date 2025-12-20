from sqlmodel import create_engine, Session
from app.core.config import settings

# check_same_thread=False 是 SQLite 必须的
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args,echo=True)

def get_session():
    with Session(engine) as session:
        yield session