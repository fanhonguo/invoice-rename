"""测试日志模块"""
import os
from src.logger import InvoiceLogger


def test_logger():
    """测试日志记录器"""
    logger = InvoiceLogger("test.log")

    logger.log_success("old.pdf", "new.pdf")
    logger.log_failure("fail.pdf", "无法读取")

    assert logger.success_count == 1
    assert logger.failure_count == 1
    assert len(logger.entries) == 2

    logger.save_to_file()
    assert os.path.exists("test.log")

    # 清理
    os.remove("test.log")
