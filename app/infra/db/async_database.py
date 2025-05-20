from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.config.settings import settings

# 创建Base类，所有模型类都将继承这个类
Base = declarative_base()

# 异步数据库URL
ASYNC_DATABASE_URL = f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Only echo SQL in debug mode
    pool_recycle=3600,  # Recycle connections every hour
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max overflow connections
    pool_use_lifo=True,  # 使用 LIFO 策略，让最近使用的连接被优先返回，这样不活跃的连接更可能被自动清理
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 异步数据库会话依赖
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # Commit session if no exceptions
    except Exception:
        await session.rollback()  # Rollback on exceptions
        raise
    finally:
        # 确保会话被正确关闭
        try:
            # 在关闭会话之前，显式关闭会话的所有连接
            # 这可以减少 Connection.__del__ 中的错误
            conn = await session.connection()
            raw_conn = conn.engine.raw_connection
            if hasattr(raw_conn, "_connection") and raw_conn._connection:
                if not raw_conn._connection._closed:
                    await raw_conn._connection.ensure_closed()
        except Exception as e:
            # 记录错误但继续执行
            import logging

            logging.getLogger("app.infra.db").error(
                f"Error pre-closing connection: {e}"
            )

        try:
            await session.close()  # 确保会话被关闭
        except Exception as e:
            # 记录错误但继续执行
            import logging

            logging.getLogger("app.infra.db").error(f"Error closing session: {e}")
