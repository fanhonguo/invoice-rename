"""测试PDF文本提取模块"""
import pytest
from pdf_extractor import extract_text_from_pdf

def test_extract_text_from_pdf():
    """测试从PDF提取文本"""
    # 这里需要一个测试PDF文件
    # 实际使用时需要创建一个测试PDF
    result = extract_text_from_pdf("test_invoice.pdf")
    assert result is not None
    assert "销售方：" in result or "销售方:" in result

def test_extract_text_from_invalid_pdf():
    """测试无效PDF文件"""
    result = extract_text_from_pdf("nonexistent.pdf")
    assert result is None
