import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv



load_dotenv()  # 默认查找当前工作目录及其父目录的 .env




class Settings(BaseSettings):
    PROJECT_NAME: str = "Training Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-super-secret-key-change-it"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30   # 单位是分钟 因此60 * 24 1天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "./media/db/training_platform.db"


    class Config:
        case_sensitive = True


settings = Settings()



if __name__=='__main__':
    print(settings.PROJECT_NAME)
    print(settings.API_V1_STR)
    print(settings.SECRET_KEY)
    print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    print(settings.DATABASE_URL)
