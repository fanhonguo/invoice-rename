"""测试发票字段解析模块"""
import pytest
from invoice_parser import parse_invoice, clean_value


def test_parse_invoice_success():
    """测试成功解析发票"""
    text = """
    购买方：测试公司
    销售方：某某科技有限公司发票号码：12345678
    """
    result = parse_invoice(text)
    assert result is not None
    assert result["seller"] == "某某科技有限公司"
    assert result["invoice_no"] == "12345678"


def test_parse_invoice_no_space():
    """测试无冒号空格的格式"""
    text = "销售方:ABC公司发票号码:87654321"
    result = parse_invoice(text)
    assert result is not None
    assert result["seller"] == "ABC公司"
    assert result["invoice_no"] == "87654321"


def test_parse_invoice_missing_fields():
    """测试缺少字段的情况"""
    text = "这是一些文本但没有发票信息"
    result = parse_invoice(text)
    assert result is None


def test_clean_value():
    """测试清理值"""
    assert clean_value("  测试  ") == "测试"
    assert clean_value("测试\n公司") == "测试公司"
    assert clean_value("测试\r\n公司") == "测试公司"
