"""文件重命名模块"""
import os
from typing import Tuple
from src.config import INVALID_CHARS, FILENAME_SEPARATOR


def clean_filename(name: str) -> str:
    """
    清理文件名中的非法字符

    Args:
        name: 原始名称

    Returns:
        清理后的名称
    """
    # 移除Windows非法字符
    for char in INVALID_CHARS:
        name = name.replace(char, '')
    return name


def construct_new_name(
    buyer_alias: str = None,
    seller: str = "",
    invoice_no: str = "",
    date: str = None,
    is_usd: bool = False
) -> str:
    """
    构造新文件名

    Args:
        buyer_alias: 购买方简称（可选）
        seller: 销售方名称
        invoice_no: 发票号码
        date: 开票日期（可选，格式 YYYY-MM-DD）
        is_usd: 是否为 USD 付款

    Returns:
        新文件名
        格式: {购买方简称}-{销售方名称}-{发票号码}-{日期}-USD.pdf
             或 {购买方简称}-{销售方名称}-{发票号码}-{日期}.pdf
    """
    parts = []

    # 添加购买方简称（如果有）
    if buyer_alias:
        parts.append(clean_filename(buyer_alias))

    # 添加销售方名称
    parts.append(clean_filename(seller))

    # 添加发票号码
    parts.append(clean_filename(invoice_no))

    # 添加日期（如果有）
    if date:
        parts.append(clean_filename(date))

    # 添加 USD 后缀（如果需要）
    if is_usd:
        parts.append("USD")

    return FILENAME_SEPARATOR.join(parts) + ".pdf"


def rename_file(
    original_path: str,
    buyer_alias: str = None,
    seller: str = "",
    invoice_no: str = "",
    date: str = None,
    is_usd: bool = False
) -> Tuple[bool, str]:
    """
    重命名文件

    Args:
        original_path: 原文件完整路径
        buyer_alias: 购买方简称（可选）
        seller: 销售方名称
        invoice_no: 发票号码
        date: 开票日期（可选）
        is_usd: 是否为 USD 付款

    Returns:
        (成功状态, 新文件路径或错误信息)
    """
    try:
        directory = os.path.dirname(original_path)
        new_name = construct_new_name(buyer_alias, seller, invoice_no, date, is_usd)
        new_path = os.path.join(directory, new_name)

        if os.path.exists(new_path):
            return False, "目标文件已存在"

        os.rename(original_path, new_path)
        return True, new_path

    except Exception as e:
        return False, f"重命名失败: {str(e)}"
