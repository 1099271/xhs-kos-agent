"""
测试运行器 - 用于执行所有测试
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from test.test_user_analyst import test_user_analyst_agent
from test.test_multi_agent_workflow import run_all_multi_agent_tests
from test.test_llm_manager import run_all_llm_tests
from app.utils.logger import app_logger as logger


async def run_all_tests():
    """运行所有测试"""

    logger.info("开始运行 XHS KOS Agent 测试套件")

    tests = [
        ("用户分析Agent测试", test_user_analyst_agent),
        ("Multi-Agent工作流测试", run_all_multi_agent_tests),
        ("LLM模型管理器测试", run_all_llm_tests),
        # 可以在这里添加更多测试
    ]

    success_count = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"正在运行: {test_name}")
            logger.info(f"{'='*60}")

            await test_func()
            logger.info(f"✅ {test_name} - 通过")
            success_count += 1

        except Exception as e:
            logger.error(f"❌ {test_name} - 失败: {e}")
            continue

    logger.info(f"\n{'='*60}")
    logger.info(f"测试完成: {success_count}/{total_tests} 通过")
    logger.info(f"{'='*60}")

    if success_count == total_tests:
        logger.info("🎉 所有测试通过！")
        return True
    else:
        logger.warning(f"⚠️  有 {total_tests - success_count} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
