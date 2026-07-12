"""发票字段解析模块"""
import re
from typing import Optional, Dict, Any
from src.config import (
    BUYER_PATTERNS,
    INVOICE_NO_PATTERNS,
    REMARK_PATTERNS,
    SELLER_NAME_PATTERNS,
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
        - is_usd: 是否为 USD 付款
        如果提取失败返回 None
    """
    if not text:
        return None

    # 步骤1: 先提取发票号码
    invoice_no = None
    for pattern in INVOICE_NO_PATTERNS:
        match = re.search(pattern, text)
        if match:
            invoice_no = clean_value(match.group(1))
            # 验证发票号码长度（通常15-20位）
            if invoice_no and len(invoice_no) >= 15:
                break

    if not invoice_no or len(invoice_no) < 15:
        return None

    # 步骤2: 提取销售方名称（使用专门的提取函数）
    seller = extract_seller_name(text)
    if not seller:
        return None

    # 提取可选字段
    buyer_alias = extract_buyer_alias(text)
    is_usd = check_usd_payment(text)

    return {
        "seller": seller,
        "invoice_no": invoice_no,
        "buyer_alias": buyer_alias,
        "is_usd": is_usd
    }


def extract_seller_name(text: str) -> Optional[str]:
    """
    从文本中提取销售方名称

    Args:
        text: PDF 提取的文本内容

    Returns:
        销售方名称，如果未找到返回 None
    """
    if not text:
        return None

    # 方法1: 尝试标准模式
    for pattern in SELLER_NAME_PATTERNS:
        match = re.search(pattern, text)
        if match:
            seller = clean_value(match.group(1))
            if seller and len(seller) > 5:
                # 清理可能的额外信息
                seller = re.sub(r'\s*统一社会信用代码.*', '', seller)
                seller = re.sub(r'\s*9131.*', '', seller)  # 清理统一社会信用代码
                seller = seller.strip()
                if seller:
                    return seller

    # 方法2: 处理并排格式（购买方 销售方）
    # 在文本中查找两个公司名称并排的情况
    # 假设购买方在前，销售方在后（根据实际PDF格式）
    lines = text.split('\n')
    for line in lines:
        # 查找包含两个"有限公司"或类似的行
        companies = re.findall(r'([^0-9\s]{5,30}?有限公司|[^0-9\s]{5,30}?物流|[^0-9\s]{5,30}?代理|[^0-9\s]{5,30}?科技)', line)
        if len(companies) >= 2:
            # 取第二个作为销售方（通常格式是：购买方 销售方）
            seller = companies[1].strip()
            if len(seller) > 5:
                return seller

    # 方法3: 在包含已知购买方的行中查找销售方
    for buyer_name in BUYER_ALIAS_MAP.values():
        # 查找包含购买方的行
        for line in lines:
            if buyer_name in line:
                # 尝试提取同一行中的另一个公司名称
                # 使用排除法：排除购买方名称
                remaining = line.replace(buyer_name, '')
                # 在剩余部分查找公司名称
                seller_match = re.search(r'([^0-9\s]{5,30}?有限公司|[^0-9\s]{5,30}?物流|[^0-9\s]{5,30}?代理)', remaining)
                if seller_match:
                    seller = seller_match.group(1).strip()
                    if len(seller) > 5:
                        return seller

    return None
