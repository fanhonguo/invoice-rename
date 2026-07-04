"""文件重命名模块"""
import os
from typing import Tuple
from config import INVALID_CHARS


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


def construct_new_name(seller: str, invoice_no: str) -> str:
    """
    构造新文件名

    Args:
        seller: 销售方名称
        invoice_no: 发票号码

    Returns:
        新文件名（格式：销售方名称 发票号码.pdf）
    """
    clean_seller = clean_filename(seller)
    clean_invoice = clean_filename(invoice_no)
    return f"{clean_seller} {clean_invoice}.pdf"


def rename_file(original_path: str, seller: str, invoice_no: str) -> Tuple[bool, str]:
    """
    重命名文件

    Args:
        original_path: 原文件完整路径
        seller: 销售方名称
        invoice_no: 发票号码

    Returns:
        (成功状态, 新文件路径或错误信息)
    """
    try:
        # 获取目录和原文件名
        directory = os.path.dirname(original_path)
        new_name = construct_new_name(seller, invoice_no)
        new_path = os.path.join(directory, new_name)

        # 检查目标文件是否已存在
        if os.path.exists(new_path):
            return False, "目标文件已存在"

        # 执行重命名
        os.rename(original_path, new_path)
        return True, new_path

    except Exception as e:
        return False, f"重命名失败: {str(e)}"
