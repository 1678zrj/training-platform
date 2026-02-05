from pydantic_settings import BaseSettings
# from dotenv import load_dotenv


# 这行代码会把 .env 加载到环境变量，这样一来下面的配置就能够自动读取了
# 默认查找当前工作目录及其父目录 .env
# load_dotenv()  将其注释是因为通过下面配置env_file即可实现自动读取



# 读取优先级：环境变量 > .env > 成员变量默认值
class Settings(BaseSettings):
    PROJECT_NAME: str = "Training Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-super-secret-key-change-it"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30   # 单位是分钟 因此60 * 24 1天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "./media/db/training_platform.db"
    class Config:
        case_sensitive = True
        # 核心修改：直接在这里指定文件，Pydantic 会自己去读
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 忽略.env文件中多出的字段，不加这个会报错
        extra = "ignore"


settings = Settings()



if __name__=='__main__':
    print(settings.PROJECT_NAME)
    print(settings.API_V1_STR)
    print(settings.SECRET_KEY)
    print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    print(settings.DATABASE_URL)
    print(settings.ALGORITHM)