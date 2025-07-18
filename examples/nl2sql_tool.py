import os
import json
import pandas as pd
import asyncio
from typing import Annotated, Optional, Any
from typing_extensions import TypedDict
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.utils.logger import app_logger as logger
from app.infra.db.async_database import AsyncSessionLocal

description = """
当用户需要进行数据库查询工作时，请调用该函数。
完成数据查询相关工作该函数用于在指定MySQL服务器上运行一段SQL代码:
并且当前函数是使用异步aiomysql连接MySQL数据库。
本函数只负责运行SQL代码并进行数据查询，若要进行数据提取，则使用另一个extract data函数，
"""


# 输入验证函数
def validate_sql_input(sql: str) -> tuple[bool, str]:
    """验证SQL输入"""
    if not sql or not sql.strip():
        return False, "SQL语句不能为空"
    if len(sql.strip()) > 10000:  # 限制SQL长度
        return False, "SQL语句过长，请限制在10000字符以内"
    return True, ""


def validate_variable_name(var_name: str) -> tuple[bool, str]:
    """验证Python变量名"""
    import keyword
    import re

    if not var_name or not var_name.strip():
        return False, "变量名不能为空"

    var_name = var_name.strip()

    # 检查是否是有效的Python标识符
    if not var_name.isidentifier():
        return False, f"'{var_name}' 不是有效的Python变量名"

    # 检查是否是Python关键字
    if keyword.iskeyword(var_name):
        return False, f"'{var_name}' 是Python关键字，不能用作变量名"

    # 避免覆盖内置变量
    builtin_names = ["df", "pd", "np", "plt", "json", "os", "sys"]
    if var_name in builtin_names:
        return False, f"'{var_name}' 是常用库名，建议使用其他变量名"

    return True, ""


def validate_code_input(code: str) -> tuple[bool, str]:
    """验证代码输入"""
    if not code or not code.strip():
        return False, "代码不能为空"
    if len(code.strip()) > 50000:  # 限制代码长度
        return False, "代码过长，请限制在50000字符以内"
    return True, ""


class SQLQuerySchema(BaseModel):
    sql: str = Field(description=description)


async def execute_sql_with_async_db(sql: str):
    """使用异步数据库连接执行SQL（参考comment_dao.py的方式）"""
    session = AsyncSessionLocal()
    try:
        result = await session.execute(text(sql))
        rows = result.fetchall()

        # 将结果转换为pandas DataFrame，保持原有的数据处理逻辑
        if rows:
            columns = list(result.keys())
            data = [dict(zip(columns, row)) for row in rows]
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame()

        return df
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


@tool(args_schema=SQLQuerySchema)
def sql_interpreter(sql: str) -> str:
    """
    执行SQL查询并返回结果

    Args:
        sql: 要执行的SQL查询语句

    Returns:
        str: 查询结果的JSON格式字符串，包含数据和执行状态
    """
    # 输入验证
    is_valid, error_msg = validate_sql_input(sql)
    if not is_valid:
        result_data = {
            "status": "error",
            "message": f"输入验证失败: {error_msg}",
            "error_type": "validation_error",
            "error_details": error_msg,
            "data": [],
            "metadata": {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    try:
        # 记录执行的SQL
        logger.info(f"执行SQL查询: {sql[:100]}{'...' if len(sql) > 100 else ''}")

        # 使用异步数据库连接替换原有的pymysql连接
        df = asyncio.run(execute_sql_with_async_db(sql))

        # 将结果转换为标准格式
        result_data = {
            "status": "success",
            "message": f"SQL查询成功，返回 {len(df)} 行数据",
            "data": df.to_dict("records") if not df.empty else [],
            "metadata": {
                "row_count": len(df),
                "column_count": len(df.columns) if not df.empty else 0,
                "columns": df.columns.tolist() if not df.empty else [],
            },
        }

        logger.info(f"SQL查询成功，返回 {len(df)} 行数据")
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"数据库查询错误: {e}"
        logger.error(error_msg)
        result_data = {
            "status": "error",
            "message": f"SQL查询失败: {str(e)}",
            "error_type": "database_error",
            "error_details": str(e),
            "data": [],
            "metadata": {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)


# 辅助函数：安全的SQL查询（可选，用于限制危险操作）
def is_safe_sql(sql: str) -> bool:
    """
    检查SQL是否安全（仅允许SELECT查询）

    Args:
        sql: SQL查询语句

    Returns:
        bool: 如果SQL安全则返回True
    """
    sql_upper = sql.strip().upper()

    # 只允许SELECT查询
    if not sql_upper.startswith("SELECT"):
        return False

    # 检查是否包含危险关键词
    dangerous_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "REPLACE",
        "LOAD_FILE",
        "OUTFILE",
        "DUMPFILE",
    ]

    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False

    return True


@tool
def safe_sql_interpreter(sql: str) -> str:
    """
    安全的SQL查询执行器（仅允许SELECT查询）

    Args:
        sql: 要执行的SQL查询语句

    Returns:
        str: 查询结果的JSON格式字符串
    """
    # 检查SQL安全性
    if not is_safe_sql(sql):
        result_data = {
            "status": "error",
            "message": "SQL安全检查失败，只允许执行SELECT查询",
            "error_type": "security_error",
            "error_details": "禁止执行可能修改数据的SQL语句",
            "data": [],
            "metadata": {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    # 如果SQL安全，则执行查询
    return sql_interpreter(sql)


class ExtractQuerySchema(BaseModel):
    sql_query: str = Field(description="用于从 MySQL 提取数据的 SQL 查询语句。")
    df_name: str = Field(
        description="指定用于保存结果的 pandas 变量名称（字符串形式）。"
    )


@tool(args_schema=ExtractQuerySchema)
def extract_data(sql_query: str, df_name: str) -> str:
    """
    用于在MySQL数据库中提取一张表到当前Python环境中，注意，本函数只负责数据表的提取，
    并不负责数据查询，若需要在MySQL中进行数据查询，请使用sql_interpreter函数。
    同时需要注意，编写外部函数的参数消息时，必须是满足json格式的字符串。

    Args:
        sql_query: 字符串形式的SQL查询语句，用于提取MySQL中的某张表。
        df_name: 将MySQL数据库中提取的表格进行本地保存时的变量名，以字符串形式表示。

    Returns:
        str: 表格读取和保存结果
    """
    # 输入验证
    is_sql_valid, sql_error = validate_sql_input(sql_query)
    if not is_sql_valid:
        result_data = {
            "status": "error",
            "message": f"SQL输入验证失败: {sql_error}",
            "error_type": "validation_error",
            "error_details": sql_error,
            "data": {
                "variable_name": df_name,
                "sample_data": [],
            },
            "metadata": {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    is_name_valid, name_error = validate_variable_name(df_name)
    if not is_name_valid:
        result_data = {
            "status": "error",
            "message": f"变量名验证失败: {name_error}",
            "error_type": "validation_error",
            "error_details": name_error,
            "data": {
                "variable_name": df_name,
                "sample_data": [],
            },
            "metadata": {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    try:
        # 记录执行的操作
        logger.info(
            f"开始提取数据，SQL: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}, 保存为变量: {df_name}"
        )

        # 使用异步数据库连接提取数据
        df = asyncio.run(execute_sql_with_async_db(sql_query))

        # 将DataFrame保存到全局命名空间中
        globals()[df_name] = df

        # 准备返回信息（使用标准格式）
        result_data = {
            "status": "success",
            "message": f"成功提取数据到变量 '{df_name}'，包含 {len(df)} 行，{len(df.columns) if not df.empty else 0} 列",
            "data": {
                "variable_name": df_name,
                "sample_data": df.head(3).to_dict("records") if not df.empty else [],
            },
            "metadata": {
                "row_count": len(df),
                "column_count": len(df.columns) if not df.empty else 0,
                "columns": df.columns.tolist() if not df.empty else [],
            },
        }

        logger.info(f"数据提取成功，变量名: {df_name}，数据形状: {df.shape}")
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"数据提取错误: {e}"
        logger.error(error_msg)
        result_data = {
            "status": "error",
            "message": f"提取数据到变量 '{df_name}' 失败",
            "error_type": "extraction_error",
            "error_details": str(e),
            "data": {
                "variable_name": df_name,
                "sample_data": [],
            },
            "metadata": {
                "row_count": 0,
                "column_count": 0,
                "columns": [],
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)


class PythonCodeSchema(BaseModel):
    code: str = Field(description="用于执行的Python代码")


@tool(args_schema=PythonCodeSchema)
def python_interpreter(code: str) -> str:
    """
    用于执行Python代码
    """
    # 输入验证
    is_valid, error_msg = validate_code_input(code)
    if not is_valid:
        result_data = {
            "status": "error",
            "message": f"代码输入验证失败: {error_msg}",
            "error_type": "validation_error",
            "error_details": error_msg,
            "data": {
                "locals": {},
            },
            "output": {
                "stdout": "",
                "stderr": error_msg,
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    try:
        # 记录执行的代码
        logger.info(f"执行Python代码: {code[:100]}{'...' if len(code) > 100 else ''}")

        # 创建一个字典来捕获输出
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        # 创建缓冲区来捕获输出
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        # 执行代码并捕获输出 - 使用真实的全局命名空间以访问extract_data的数据
        exec_globals = globals()  # 直接使用全局命名空间，不复制
        exec_locals = {}

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, exec_globals, exec_locals)

        # 获取输出
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()

        # 准备返回结果（使用标准格式）
        result_data = {
            "status": "success",
            "message": "Python代码执行成功",
            "data": {
                "locals": {
                    k: str(v) for k, v in exec_locals.items()
                },  # 转换为字符串以便JSON序列化
            },
            "output": {
                "stdout": stdout_output if stdout_output else "",
                "stderr": stderr_output if stderr_output else "",
            },
        }

        logger.info("Python代码执行成功")
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Python代码执行错误: {e}"
        logger.error(error_msg)
        result_data = {
            "status": "error",
            "message": "Python代码执行失败",
            "error_type": "execution_error",
            "error_details": str(e),
            "data": {
                "locals": {},
            },
            "output": {
                "stdout": "",
                "stderr": str(e),
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)


class FigCodeSchema(BaseModel):
    code: str = Field(description="用于生成图表的Python代码")
    save_directory: Optional[str] = Field(
        default=None,
        description="图片保存目录，默认为当前目录下的generated_charts文件夹",
    )


@tool(args_schema=FigCodeSchema)
def fig_interpreter(code: str, save_directory: Optional[str] = None) -> str:
    """
    用于执行绘图类的Python代码，支持matplotlib、seaborn等绘图库

    Args:
        code: 用于生成图表的Python代码
        save_directory: 图片保存目录，默认为当前目录下的generated_charts文件夹

    Returns:
        str: 包含执行结果、图片base64编码和保存路径的JSON字符串
    """
    # 输入验证
    is_valid, error_msg = validate_code_input(code)
    if not is_valid:
        result_data = {
            "status": "error",
            "message": f"绘图代码输入验证失败: {error_msg}",
            "error_type": "validation_error",
            "error_details": error_msg,
            "data": {
                "image_base64": "",
                "saved_path": "",
                "relative_path": "",
                "filename": "",
                "charts_directory": "",
                "locals": {},
            },
            "output": {
                "stdout": "",
                "stderr": error_msg,
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    try:
        # 记录执行的代码
        logger.info(f"执行绘图代码: {code[:100]}{'...' if len(code) > 100 else ''}")

        import io
        import sys
        import matplotlib
        import matplotlib.pyplot as plt
        import base64
        from contextlib import redirect_stdout, redirect_stderr

        # 设置matplotlib后端为Agg（非交互式）
        matplotlib.use("Agg")

        # 创建缓冲区来捕获输出
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        # 执行代码并捕获输出 - 使用真实的全局命名空间以访问extract_data的数据
        exec_globals = globals()  # 直接使用全局命名空间，不复制
        exec_globals.update({"plt": plt, "matplotlib": matplotlib})
        exec_locals = {}

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, exec_globals, exec_locals)

        # 获取输出
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()

        # 创建图片保存目录
        from datetime import datetime
        import os

        # 设置图片保存目录
        if save_directory:
            charts_dir = os.path.abspath(save_directory)
        else:
            charts_dir = os.path.join(os.getcwd(), "generated_charts")

        # 创建目录（如果不存在）
        try:
            os.makedirs(charts_dir, exist_ok=True)
        except Exception as dir_error:
            error_msg = f"创建保存目录失败: {str(dir_error)}"
            logger.error(error_msg)
            result_data = {
                "status": "error",
                "message": error_msg,
                "error_type": "directory_error",
                "error_details": str(dir_error),
                "data": {
                    "image_base64": "",
                    "saved_path": "",
                    "relative_path": "",
                    "filename": "",
                    "charts_directory": save_directory or charts_dir,
                    "locals": {},
                },
                "output": {
                    "stdout": "",
                    "stderr": error_msg,
                },
            }
            return json.dumps(result_data, ensure_ascii=False, indent=2)

        # 生成唯一的文件名（基于时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 精确到毫秒
        filename = f"chart_{timestamp}.png"
        file_path = os.path.join(charts_dir, filename)

        # 保存图像到文件
        try:
            plt.savefig(file_path, format="png", dpi=300, bbox_inches="tight")
            logger.info(f"图片已保存到: {file_path}")
        except Exception as save_error:
            error_msg = f"保存图片文件失败: {str(save_error)}"
            logger.error(error_msg)
            plt.close("all")  # 确保清理matplotlib
            result_data = {
                "status": "error",
                "message": error_msg,
                "error_type": "file_save_error",
                "error_details": str(save_error),
                "data": {
                    "image_base64": "",
                    "saved_path": "",
                    "relative_path": "",
                    "filename": filename,
                    "charts_directory": charts_dir,
                    "locals": {k: str(v) for k, v in exec_locals.items()},
                },
                "output": {
                    "stdout": stdout_output if stdout_output else "",
                    "stderr": stderr_output if stderr_output else "",
                },
            }
            return json.dumps(result_data, ensure_ascii=False, indent=2)

        # 同时保存图像到字节流（保持向后兼容）
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
        img_buffer.seek(0)

        # 将图像编码为base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

        # 清理matplotlib
        plt.close("all")

        # 获取相对路径（更友好的显示）
        try:
            relative_path = os.path.relpath(file_path, os.getcwd())
        except ValueError:
            relative_path = file_path  # 如果无法获取相对路径，使用绝对路径

        # 准备返回结果（使用标准格式，包含保存路径）
        result_data = {
            "status": "success",
            "message": f"绘图代码执行成功，图像已生成并保存到: {relative_path}",
            "data": {
                "image_base64": img_base64,
                "saved_path": file_path,  # 绝对路径
                "relative_path": relative_path,  # 相对路径
                "filename": filename,
                "charts_directory": charts_dir,
                "locals": {k: str(v) for k, v in exec_locals.items()},
            },
            "output": {
                "stdout": stdout_output if stdout_output else "",
                "stderr": stderr_output if stderr_output else "",
            },
        }

        logger.info("绘图代码执行成功")
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"绘图代码执行错误: {e}"
        logger.error(error_msg)

        # 确保清理matplotlib
        try:
            import matplotlib.pyplot as plt

            plt.close("all")
        except:
            pass

        result_data = {
            "status": "error",
            "message": "绘图代码执行失败",
            "error_type": "execution_error",
            "error_details": str(e),
            "data": {
                "image_base64": "",
                "saved_path": "",
                "relative_path": "",
                "filename": "",
                "charts_directory": "",
                "locals": {},
            },
            "output": {
                "stdout": "",
                "stderr": str(e),
            },
        }
        return json.dumps(result_data, ensure_ascii=False, indent=2)
