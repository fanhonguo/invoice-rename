"""测试重命名模块"""
import pytest
from renamer import clean_filename, construct_new_name


def test_clean_filename():
    """测试清理文件名中的非法字符"""
    # 测试Windows非法字符
    assert clean_filename('测试<公司>') == '测试公司'
    assert clean_filename('A:B/C|D*E?F') == 'ABCDEF'
    # 测试保留正常字符
    assert clean_filename('正常公司123') == '正常公司123'
    # 测试保留空格
    assert clean_filename('公司 A 公司') == '公司 A 公司'


def test_construct_new_name():
    """测试构造新文件名"""
    result = construct_new_name("测试公司", "12345678")
    assert result == "测试公司 12345678.pdf"

    # 测试带特殊字符的发票号码
    result = construct_new_name("ABC公司", "No.12345")
    assert result == "ABC公司 No.12345.pdf"
