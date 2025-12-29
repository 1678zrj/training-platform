import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv



load_dotenv()  # 默认查找当前工作目录及其父目录的 .env

class Settings(BaseSettings):
    PROJECT_NAME: str = "Training Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./media/db/database.db")

    class Config:
        case_sensitive = True


settings = Settings()



if __name__=='__main__':
    print(settings.DATABASE_URL)