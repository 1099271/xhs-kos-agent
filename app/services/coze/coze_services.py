from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Callable,
    AsyncGenerator,
    TypeVar,
)
import time
import json
import traceback
import requests

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.utils.logger import app_logger as logger
from app.utils.file import save_json_response
from app.infra.db.async_database import get_async_db
from app.infra.models.topic_models import XhsTopicsResponse

T = TypeVar("T")


class CozeService:

    max_retries = 5

    def __init__(self):
        pass

    def call_coze_api(
        self,
        workflow_id: str,
        parameters: Dict[str, Any],
        log_file_prefix: str,
        retries: int = 0,
    ) -> Dict[str, Any]:
        """
        调用Coze API并保存响应

        Args:
            workflow_id: 工作流ID
            parameters: API参数
            log_file_prefix: log文件前缀
            retries: 当前重试次数

        Returns:
            API响应结果
        """
        if retries >= self.max_retries:
            logger.error(
                f"调用Coze API达到最大重试次数 {self.max_retries} 后失败 (workflow_id: {workflow_id})."
            )
            return {
                "error": "Max retries reached",
                "code": -1,
                "msg": "达到最大重试次数",
            }

        url = "https://api.coze.cn/v1/workflow/run"
        headers = {
            "Authorization": f"Bearer {settings.COZE_API_TOKEN}",
            "Content-Type": "application/json",
        }

        # 确保cookie存在于参数中
        if "cookie" not in parameters:
            parameters["cookie"] = settings.XHS_COOKIE

        payload = {"parameters": parameters, "workflow_id": workflow_id}

        try:
            # latest_log = "logs/coze_http_request/20250520/174508932529.log"
            # with open(latest_log, "r", encoding="utf-8") as f:
            #     resp_json = json.load(f)

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # 如果请求失败，抛出异常
            resp_json = response.json()
            save_json_response(resp_json, log_file_prefix="coze_http_request")

            # 根据响应状态码处理逻辑
            match resp_json.get("code"):
                case 4013:
                    # 请求频率超出限制，等待60秒后重试
                    logger.warning(
                        f"Coze API请求频率超出限制 (workflow_id: {workflow_id}), 将在60秒后重试 (当前重试次数: {retries + 1})"
                    )
                    time.sleep(60)
                    return self.call_coze_api(
                        workflow_id, parameters, log_file_prefix, retries + 1
                    )
                case 720702222:
                    # We're currently experiencing server issues. Please try your request again after a short delay. If the problem persists, contact our support team.
                    logger.warning(
                        f"Coze API服务器问题 (workflow_id: {workflow_id}), 将在120秒后重试 (当前重试次数: {retries + 1})"
                    )
                    time.sleep(120)
                    return self.call_coze_api(
                        workflow_id, parameters, log_file_prefix, retries + 1
                    )
                case _:
                    if resp_json.get("code") != 0:
                        logger.error(
                            f"请求Coze出现异常:{resp_json.get('code')}|{resp_json.get('msg')}"
                        )
                    return resp_json

        except Exception as e:
            logger.error(f"调用Coze API失败: {e}")
            traceback.print_exc()
            return {}

    @staticmethod
    def process_response(
        result: Dict[str, Any], response_type: Type[T]
    ) -> Tuple[Optional[T], Dict[str, Any]]:
        """
        处理API响应并解析数据

        Args:
            result: API响应结果
            response_type: 响应对象类型

        Returns:
            解析后的响应对象和请求信息
        """
        if not isinstance(result["data"], str):
            logger.error("data字段不是字符串")
            logger.info(
                "返回的完整数据:", json.dumps(result, ensure_ascii=False, indent=2)
            )
            return None, {}

        try:
            # 检查字符串是否为空
            if not result["data"]:
                logger.error("data字段为空")
                return None, {}

            # 替换中文逗号为英文逗号
            data_json = json.loads(result["data"])

            # 检查resp_data字段
            if "resp_data" in data_json:
                resp_data = data_json["resp_data"]

                # 创建响应对象
                if response_type == XhsTopicsResponse:
                    response_obj = response_type(
                        code=data_json.get("resp_code", 0), data=resp_data
                    )
                else:
                    response_obj = response_type(
                        status=data_json.get("resp_code", 0), data=resp_data
                    )

                return response_obj, data_json
            else:
                logger.error(
                    "未找到resp_data字段,data字段内容:",
                    json.dumps(data_json, ensure_ascii=False, indent=2),
                )
                return None, {}

        except json.JSONDecodeError as e:
            logger.error(f"data字段JSON解析错误: {e}")
            logger.error("data字段内容:", result["data"])  # 打印原始字符串以便调试
            return None, {}

    @staticmethod
    async def store_data_in_db(
        db_method: Callable[..., AsyncGenerator[List[Any], Any]],
        req_info: Dict[str, Any],
        response_obj: Any,
        data_type: str = "笔记",
    ) -> List[Any]:
        """
        将数据存储到数据库 (异步)

        Args:
            db_method: 异步数据库操作方法
            req_info: 请求信息
            response_obj: 响应对象
            data_type: 数据类型描述

        Returns:
            存储的数据列表
        """
        stored_data = []
        async for session in get_async_db():
            db: AsyncSession = session
            try:
                stored_data = await db_method(db, req_info, response_obj)
                logger.info(
                    f"成功存储 {len(stored_data) if isinstance(stored_data, list) else 1} 条{data_type}数据到数据库"
                )

            except Exception as e:
                logger.error(f"存储{data_type}数据到数据库时出错: {e}")
                traceback.print_exc()
            break

        return stored_data
