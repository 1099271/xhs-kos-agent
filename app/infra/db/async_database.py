from typing import AsyncGenerator
import atexit
import asyncio
import weakref
import signal
import os

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


class DatabaseManager:
    """数据库管理器 - 统一处理连接清理问题"""
    
    _instance = None
    _initialized = False
    _engine_disposed = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cleanup_registered = False
            self._register_cleanup()
            DatabaseManager._initialized = True
    
    def _register_cleanup(self):
        """注册程序退出时的清理函数"""
        if not self._cleanup_registered:
            # 注册多种清理机制
            atexit.register(self._emergency_cleanup)
            
            # 注册信号处理器（用于Ctrl+C等）
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, self._signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, self._signal_handler)
            
            self._cleanup_registered = True
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self._emergency_cleanup()
        # 继续默认的信号处理
        signal.default_int_handler(signum, frame)
    
    def _emergency_cleanup(self):
        """紧急清理函数，仅在进程即将退出时调用"""
        if not self._engine_disposed:
            try:
                # 尝试同步关闭引擎（如果可能的话）
                engine = async_engine
                if engine and hasattr(engine, 'sync_engine'):
                    # 对于AsyncEngine，尝试访问底层的同步引擎
                    sync_engine = engine.sync_engine
                    if sync_engine:
                        sync_engine.dispose()
                        self._engine_disposed = True
            except Exception:
                pass  # 静默处理所有错误
    
    async def cleanup(self):
        """手动清理数据库连接"""
        if not self._engine_disposed:
            try:
                await async_engine.dispose()
                self._engine_disposed = True
            except Exception:
                pass  # 静默处理清理错误


# 创建全局数据库管理器实例 - 这会自动注册清理函数
db_manager = DatabaseManager()


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
        await session.close()


async def get_async_session() -> AsyncSession:
    """
    获取异步数据库会话的便捷函数
    使用方式:
    
    session = await get_async_session()
    try:
        # 数据库操作
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
    """
    return AsyncSessionLocal()


# 上下文管理器版本
class AsyncSessionContext:
    """异步会话上下文管理器"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type is None:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()


def get_session_context() -> AsyncSessionContext:
    """
    获取异步会话上下文管理器
    使用方式:
    
    async with get_session_context() as session:
        # 数据库操作
        result = await session.execute(query)
    """
    return AsyncSessionContext()
