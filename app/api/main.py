"""
Multi-Agent系统的FastAPI主应用
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.api.routers.agent_routes import router as agent_router
from app.utils.logger import app_logger as logger


# 创建FastAPI应用
app = FastAPI(
    title="XHS KOS Multi-Agent系统",
    description="基于小红书数据的智能Multi-Agent内容策略和内容生成系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该配置具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": str(logging.Formatter().formatTime(logging.LogRecord(
                name="error", level=logging.ERROR, pathname="", lineno=0,
                msg=str(exc), args=(), exc_info=None
            )))
        }
    )


# 路由注册
app.include_router(agent_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "XHS KOS Multi-Agent系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/agents/health",
        "endpoints": {
            "strategy": "/api/v1/agents/strategy",
            "content": "/api/v1/agents/content",
            "workflow": "/api/v1/agents/workflow",
            "users": "/api/v1/agents/users"
        }
    }


@app.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": str(logging.Formatter().formatTime(logging.LogRecord(
            name="health", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))),
        "service": "XHS KOS Multi-Agent系统",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 XHS KOS Multi-Agent系统启动中...")
    
    # 初始化Agent
    try:
        from app.agents.strategy_coordinator_agent import StrategyCoordinatorAgent
        from app.agents.content_generator_agent import ContentGeneratorAgent
        from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent
        from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow
        
        # 预加载Agent实例
        coordinator = StrategyCoordinatorAgent()
        content_gen = ContentGeneratorAgent()
        analyst = EnhancedUserAnalystAgent()
        workflow = EnhancedMultiAgentWorkflow()
        
        logger.info("✅ 所有Agent初始化完成")
        
    except Exception as e:
        logger.error(f"❌ Agent初始化失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 XHS KOS Multi-Agent系统关闭中...")
    
    # 清理资源
    try:
        from app.infra.db.async_database import async_engine
        await async_engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")


# 运行应用的主函数
def run_app(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """运行FastAPI应用"""
    
    config = {
        "host": host,
        "port": port,
        "reload": reload,
        "log_level": "info"
    }
    
    if reload:
        uvicorn.run("app.api.main:app", **config)
    else:
        uvicorn.run(app, **config)


if __name__ == "__main__":
    # 直接运行时的配置
    run_app(reload=True)