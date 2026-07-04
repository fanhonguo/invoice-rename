"""发票字段解析模块"""
import re
from typing import Optional, Dict, Any
from src.config import (
    SELLER_PATTERNS,
    BUYER_PATTERNS,
    INVOICE_NO_PATTERNS,
    REMARK_PATTERNS,
    DATE_PATTERNS,
    BUYER_ALIAS_MAP,
    USD_KEYWORDS
)


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


def extract_buyer_alias(text: str) -> Optional[str]:
    """
    从文本中提取购买方简称

    Args:
        text: PDF 提取的文本内容

    Returns:
        购买方简称，如果不在映射表中返回 None
    """
    if not text:
        return None

    for pattern in BUYER_PATTERNS:
        match = re.search(pattern, text)
        if match:
            buyer_name = clean_value(match.group(1))
            # 从映射表中查找简称
            return BUYER_ALIAS_MAP.get(buyer_name)

    return None


def extract_invoice_date(text: str) -> Optional[str]:
    """
    从文本中提取开票日期

    Args:
        text: PDF 提取的文本内容

    Returns:
        标准格式的日期字符串 (YYYY-MM-DD)，如果未找到返回 None
    """
    if not text:
        return None

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                year, month, day = groups
                # 标准化为 YYYY-MM-DD 格式
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return None


def check_usd_payment(text: str) -> bool:
    """
    检查文本是否包含 USD 付款关键词

    Args:
        text: PDF 提取的文本内容

    Returns:
        如果包含 USD 关键词返回 True
    """
    if not text:
        return False

    # 先检查备注中的内容
    for pattern in REMARK_PATTERNS:
        match = re.search(pattern, text)
        if match:
            remark = match.group(1)
            # 检查备注中的关键词
            for keyword in USD_KEYWORDS:
                if keyword in remark:
                    return True
            return False  # 找到备注但没关键词，不再检查

    # 如果没有备注，检查整个文本
    for keyword in USD_KEYWORDS:
        if keyword in text:
            return True

    return False


def parse_invoice(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取发票所有字段

    Args:
        text: PDF 提取的文本内容

    Returns:
        包含以下字段的字典:
        - seller: 销售方名称
        - invoice_no: 发票号码
        - buyer_alias: 购买方简称 (可选)
        - date: 开票日期 (可选)
        - is_usd: 是否为 USD 付款
        如果提取失败返回 None
    """
    if not text:
        return None

    # 提取销售方名称和发票号码
    seller = None
    invoice_no = None

    for pattern in SELLER_PATTERNS:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            invoice_no = clean_value(match.group(1))
            seller = clean_value(match.group(2))
            if seller and invoice_no:
                break

    if not seller or not invoice_no:
        return None

    # 提取可选字段
    buyer_alias = extract_buyer_alias(text)
    date = extract_invoice_date(text)
    is_usd = check_usd_payment(text)

    return {
        "seller": seller,
        "invoice_no": invoice_no,
        "buyer_alias": buyer_alias,
        "date": date,
        "is_usd": is_usd
    }
