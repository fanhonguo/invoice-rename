"""测试重命名模块"""
import pytest
from src.renamer import clean_filename, construct_new_name


def test_clean_filename():
    """测试清理文件名中的非法字符"""
    # 测试Windows非法字符
    assert clean_filename('测试<公司>') == '测试公司'
    assert clean_filename('A:B/C|D*E?F') == 'ABCDEF'
    # 测试保留正常字符
    assert clean_filename('正常公司123') == '正常公司123'
    # 测试保留连字符
    assert clean_filename('公司-A-公司') == '公司-A-公司'


def test_construct_new_name_full():
    """测试完整的新文件名格式"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        is_usd=True
    )
    assert result == "昊奕佳-美设国际物流集团股份有限公司-1657614422-USD.pdf"


def test_construct_new_name_without_usd():
    """测试不含 USD 的文件名"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        is_usd=False
    )
    assert result == "昊奕佳-美设国际物流集团股份有限公司-1657614422.pdf"


def test_construct_new_name_no_buyer_alias():
    """测试没有购买方简称的文件名"""
    result = construct_new_name(
        buyer_alias=None,
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        is_usd=False
    )
    assert result == "美设国际物流集团股份有限公司-1657614422.pdf"


def test_construct_new_name_with_usd_no_buyer():
    """测试有 USD 但没有购买方简称的文件名"""
    result = construct_new_name(
        buyer_alias=None,
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        is_usd=True
    )
    assert result == "美设国际物流集团股份有限公司-1657614422-USD.pdf"


def test_construct_new_name_minimal():
    """测试最小文件名（只有销售方和发票号）"""
    result = construct_new_name(
        buyer_alias=None,
        seller="美设公司",
        invoice_no="12345",
        is_usd=False
    )
    assert result == "美设公司-12345.pdf"


def test_construct_new_name_with_invalid_chars():
    """测试含非法字符的文件名清理"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设<国际>物流",
        invoice_no="12345",
        is_usd=False
    )
    assert result == "昊奕佳-美设国际物流-12345.pdf"
