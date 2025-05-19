import os
import sys
from pathlib import Path

from loguru import logger as loguru_logger
from rich import print as rich_print

# 移除默认的loguru处理器
loguru_logger.remove()

# 保存原始logger对象用于后续使用
app_logger = loguru_logger


def setup_logger(name="root", level="INFO", log_file_path=None):
    """
    设置日志配置，现在使用loguru实现

    Args:
        name: 日志名称
        level: 日志级别
        log_file_path: 日志文件路径
    """
    # 首先移除所有现有的handler
    loguru_logger.remove()

    # 添加控制台输出处理器
    loguru_logger.add(
        sys.stdout,
        level=level,
        colorize=True,
    )

    # 如果指定了日志文件，添加文件处理器
    if log_file_path:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 添加文件处理器
        loguru_logger.add(
            log_file_path,
            level=level,
            rotation="10 MB",  # 文件达到10MB时轮换
            retention=5,  # 保留5个备份
            compression="zip",  # 压缩备份文件
        )

    return loguru_logger


def get_logger(name):
    """
    获取配置好的日志器

    Args:
        name: 日志器名称

    Returns:
        Logger: 配置好的loguru实例
    """
    # loguru不需要为每个模块创建logger实例，只需返回原始实例
    # 但我们可以设置上下文信息
    return loguru_logger.bind(name=name)


# # 便捷的日志记录函数 - 维持与原有API兼容
# def debug(msg, *args, **kwargs):
#     """Debug级别日志"""
#     loguru_logger.opt(depth=1).debug(msg, *args, **kwargs)


# def info(msg, *args, **kwargs):
#     """Info级别日志"""
#     loguru_logger.opt(depth=1).info(msg, *args, **kwargs)


# def warning(msg, *args, **kwargs):
#     """Warning级别日志"""
#     loguru_logger.opt(depth=1).warning(msg, *args, **kwargs)


# def error(msg, *args, **kwargs):
#     """Error级别日志"""
#     loguru_logger.opt(depth=1).error(msg, *args, **kwargs)


# def critical(msg, *args, **kwargs):
#     """Critical级别日志"""
#     loguru_logger.opt(depth=1).critical(msg, *args, **kwargs)


def pprint(obj):
    """打印对象"""
    rich_print(obj)
