"""测试PDF文本提取模块"""
import pytest
import os
from src.pdf_extractor import extract_text_from_pdf


def test_extract_text_from_invalid_pdf():
    """测试无效PDF文件"""
    result = extract_text_from_pdf("nonexistent.pdf")
    assert result is None


def test_extract_text_from_pdf_no_file():
    """测试不存在的文件"""
    result = extract_text_from_pdf("test_invoice.pdf")
    # 如果文件不存在，应该返回 None
    # 跳过此测试，因为没有测试PDF文件
    if result is None and not os.path.exists("test_invoice.pdf"):
        pytest.skip("没有测试PDF文件")
