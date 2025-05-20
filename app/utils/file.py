import json
import os
from datetime import datetime
from typing import Any  # 导入 Any

from app.utils.logger import app_logger as logger


def save_json_response(data_to_save: Any, log_file_prefix: str = "generic"):
    """
    将数据保存到带有日期和时间戳的文件中。
    会尝试将数据保存为 JSON 格式，如果失败则保存为普通字符串。
    如果保存过程中发生任何错误，将记录警告日志并静默返回。

    Args:
        data_to_save: 要保存的数据 (任何类型).
        log_file_prefix: 特定日志类型的子目录前缀 (默认为 'generic').
    """
    filename = ""  # 初始化 filename 以便在 finally 中使用
    try:
        # 获取当前日期和时间戳
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        timestamp_str = now.strftime("%H%M%S%f")  # 添加微秒以增强唯一性
        full_log_dir = os.path.join("logs", log_file_prefix, date_str)

        os.makedirs(full_log_dir, exist_ok=True)

        filename = os.path.join(full_log_dir, f"{timestamp_str}.log")  # 默认用 .log
        logger.info(f"{filename}已经保存")

        # 保存数据到文件
        with open(filename, "w", encoding="utf-8") as f:
            try:
                # 尝试作为 JSON 保存
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                # 如果成功保存为 JSON，可以考虑将文件重命名为 .json
                # 但为了简化，我们统一使用 .log 或在下面记录信息
                # logger.info(f"Data successfully saved as JSON to: {filename}")
            except TypeError:
                # 如果 JSON 序列化失败，作为普通字符串保存
                # logger.info(f"Data is not JSON serializable, saving as plain string to: {filename}")
                f.seek(0)  # 回到文件开头
                f.truncate()  # 清空可能已写入的部分 JSON
                f.write(str(data_to_save))
                # logger.info(f"Data successfully saved as plain string to: {filename}")

        return filename
    except Exception as e:
        # 捕获所有可能的异常 (权限、IO错误等)
        log_filename = filename if filename else "unknown file"
        logger.warning(
            f"Error saving data to {log_filename} (prefix: {log_file_prefix}): {e}",
            exc_info=False,
        )
