import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 加载.env文件中的环境变量
load_dotenv()


class Settings(BaseSettings):
    # 应用设置
    APP_NAME: str = "xhs-kos-agent"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # 前端URL
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

    # 数据库设置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "xhs-kos-agent")

    # 安全设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # 邮件设置
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@example.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", APP_NAME)
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    MAIL_USE_CREDENTIALS: bool = (
        os.getenv("MAIL_USE_CREDENTIALS", "True").lower() == "true"
    )
    MAIL_VALIDATE_CERTS: bool = (
        os.getenv("MAIL_VALIDATE_CERTS", "True").lower() == "true"
    )

    # 登录安全配置
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_COOLDOWN_MINUTES: int = int(os.getenv("LOGIN_COOLDOWN_MINUTES", "15"))

    # coze api
    COZE_API_TOKEN: str = os.getenv("COZE_API_TOKEN", "your-secret-key-here")

    # 小红书设置
    XHS_COOKIE: str = os.getenv("XHS_COOKIE")

    # 模型设置
    QWEN_MODEL_API_KEY: str = os.getenv("QWEN_MODEL_API_KEY")
    QWEN_MODEL_NAME: str = os.getenv("QWEN_MODEL_NAME")
    QWEN_MODEL_BASE_URL: str = os.getenv("QWEN_MODEL_BASE_URL")

    # 模型设置
    DEEPSEEK_MODEL_API_KEY: str = os.getenv("DEEPSEEK_MODEL_API_KEY")
    DEEPSEEK_MODEL_NAME: str = os.getenv("DEEPSEEK_MODEL_NAME")
    DEEPSEEK_MODEL_BASE_URL: str = os.getenv("DEEPSEEK_MODEL_BASE_URL")

    # model
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    MODEL_BASE_URL: str = os.getenv("MODEL_BASE_URL")
    MODEL_API_KEY: str = os.getenv("MODEL_API_KEY")

    # api key
    OPENROUTER_KEY: str = os.getenv("OPENROUTER_KEY")
    OPENAI_KEY: str = os.getenv("OPENAI_KEY", "")
    ANTHROPIC_KEY: str = os.getenv("ANTHROPIC_KEY", "")
    ANTHROPIC_URL: str = os.getenv("ANTHROPIC_URL", "")

    # 日志设置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 系统路径设置
    PYTHONPATH: str = os.getenv("PYTHONPATH", "")
    NODE_PATH: str = os.getenv("NODE_PATH", "")

    # 关键词群组归属|picaa:Picaa透卡/fatiaoya:发条鸭/mosuo:摩梭族
    GROUP_BELONG: str = os.getenv("GROUP_BELONG", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建设置实例
settings = Settings()
