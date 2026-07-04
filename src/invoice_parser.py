"""发票字段解析模块"""
import re
from typing import Optional, Dict
from config import PATTERNS


def clean_value(value: str) -> str:
    """
    清理提取的值，去除多余空格和换行符

    Args:
        value: 原始值

    Returns:
        清理后的值
    """
    if not value:
        return ""
    # 去除首尾空格，替换换行符为空格
    value = value.strip()
    value = re.sub(r'[\r\n]+', ' ', value)
    # 去除多余空格
    value = re.sub(r'\s+', ' ', value)
    return value


def parse_invoice(text: str) -> Optional[Dict[str, str]]:
    """
    从文本中提取销售方名称和发票号码

    Args:
        text: PDF提取的文本内容

    Returns:
        包含seller和invoice_no的字典，如果提取失败返回None
    """
    if not text:
        return None

    for pattern in PATTERNS:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 新模式: invoice_no是group(1), seller是group(2)
            invoice_no = clean_value(match.group(1))
            seller = clean_value(match.group(2))

            # 验证两个字段都不为空
            if seller and invoice_no:
                return {
                    "seller": seller,
                    "invoice_no": invoice_no
                }

    return None
