"""测试发票字段解析模块"""
import pytest
from src.invoice_parser import parse_invoice, clean_value, extract_buyer_alias, extract_invoice_date, check_usd_payment


def test_parse_invoice_success():
    """测试成功解析发票（使用实际PDF格式）"""
    text = """
    发票号码：123456789012345678
    购买方名称：上海昊奕佳国际物流有限公司
    销 名称：某某科技有限公司
    """
    result = parse_invoice(text)
    assert result is not None
    assert result["seller"] == "某某科技有限公司"
    assert result["invoice_no"] == "123456789012345678"


def test_parse_invoice_missing_fields():
    """测试缺少字段的情况"""
    text = "这是一些文本但没有发票信息"
    result = parse_invoice(text)
    assert result is None


def test_clean_value():
    """测试清理值"""
    assert clean_value("  测试  ") == "测试"
    # 注意：换行符被替换为空格
    assert clean_value("测试\n公司") == "测试 公司"
    assert clean_value("测试\r\n公司") == "测试 公司"


def test_extract_buyer_alias_with_known_buyer():
    """测试已知购买方的简称提取"""
    text = "购买方名称：上海昊奕佳国际物流有限公司\n销 名称：某某公司"
    alias = extract_buyer_alias(text)
    assert alias == "昊奕佳"


def test_extract_buyer_alias_with_unknown_buyer():
    """测试未知购买方返回 None"""
    text = "购买方名称：未知公司有限公司\n销 名称：某某公司"
    alias = extract_buyer_alias(text)
    assert alias is None


def test_extract_invoice_date_standard_format():
    """测试标准日期格式提取"""
    text = "开票日期：2025-01-04\n销 名称：某某公司"
    date = extract_invoice_date(text)
    assert date == "2025-01-04"


def test_extract_invoice_date_chinese_format():
    """测试中文日期格式提取"""
    text = "开票日期：2025年1月4日\n销 名称：某某公司"
    date = extract_invoice_date(text)
    assert date == "2025-01-04"


def test_extract_invoice_date_no_date():
    """测试没有日期信息"""
    text = "销 名称：某某公司"
    date = extract_invoice_date(text)
    assert date is None


def test_check_usd_payment_with_dollar_sign():
    """测试包含美元符号"""
    text = "备注：汇率 $ 6.5"
    result = check_usd_payment(text)
    assert result is True


def test_check_usd_payment_with_exchange_rate():
    """测试包含汇率关键词"""
    text = "备注：汇率 6.5"
    result = check_usd_payment(text)
    assert result is True


def test_check_usd_payment_no_keywords():
    """测试不包含USD关键词"""
    text = "备注：普通发票"
    result = check_usd_payment(text)
    assert result is False


def test_parse_invoice_with_all_fields():
    """测试完整发票信息提取"""
    text = """
    发票号码：123456789012345678
    购买方名称：上海昊奕佳国际物流有限公司
    销 名称：某某科技有限公司
    开票日期：2025-01-04
    备注：汇率 $ 6.5
    """
    result = parse_invoice(text)
    assert result is not None
    assert result["seller"] == "某某科技有限公司"
    assert result["invoice_no"] == "123456789012345678"
    assert result["buyer_alias"] == "昊奕佳"
    assert result["date"] == "2025-01-04"
    assert result["is_usd"] is True


def test_parse_invoice_without_buyer_alias():
    """测试没有购买方简称的发票"""
    text = """
    发票号码：123456789012345678
    销 名称：某某科技有限公司
    开票日期：2025-01-04
    """
    result = parse_invoice(text)
    assert result is not None
    assert result["seller"] == "某某科技有限公司"
    assert result["invoice_no"] == "123456789012345678"
    assert result["buyer_alias"] is None
    assert result["date"] == "2025-01-04"
