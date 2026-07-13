"""配置文件"""

from typing import Dict, List

# 输入目录（默认为当前目录）
INPUT_DIR = "."

# 日志文件路径（放在logs目录）
import os
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "invoice_renamer.log")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 购买方简称映射表
BUYER_ALIAS_MAP: Dict[str, str] = {
    "上海昊奕佳国际物流有限公司": "昊奕佳",
    "上海璟易科国际物流有限公司": "璟易科",
    # 可在此添加更多映射
}

# USD 检测关键词列表
USD_KEYWORDS: List[str] = [
    "汇率",
    "$",
    "仅限",
    "只接受",
    "美金付款",
    "美元付款",
    "美金支付",
    "美元支付",
    "支付美金",
    "支付美元",
]

# 发票号码模式
INVOICE_NO_PATTERNS = [
    # 格式1: 统一发票监制后跟20位数字（最精确，支持跨行）
    r'统一发票监[\s\S]*?制[\s\S]*?(\d{20})',
    # 格式2: 标准格式 "发票号码：xxxx"（支持空格分散）
    r'发[\s\S]*?票[\s\S]*?号码[：:][\s\S]*?(\d{15,21})',
    r'发票号码[：:]\s*(\d{15,21})',
    # 格式3: 发票号码直接出现
    r'(\d{20})',
    r'(\d{19,21})',
]

# 销售方名称提取模式（在发票号码找到后）
SELLER_NAME_PATTERNS = [
    # 精确匹配：在"销 名称："和下一个字段之间
    r'销\s*名称[：:]\s*([^\r\n]+?)(?=\s*统一|\s*银行|\s*备注|\s*开票人)',
    # 备用：去除空格后匹配
    r'销名称[：:](.+?)(?:购名称|银行账号|备注|开票人|业务编号)',
    # 更宽松的匹配
    r'销\s*名称[：:]\s*([^\r\n]{5,50}?)(?:\s*$|\r|\n)',
]

# 购买方名称模式
BUYER_PATTERNS = [
    # 标准格式：购买方名称：xxx
    r'购买方名称[：:](.+?)(?:\n|$)',
    # 购名称格式
    r'购\s*名称[：:]\s*(.+?)(?:\s*$|销\s*名称|\r|\n)',
    # 并排格式：购买方 销售方（匹配映射表中的公司）
    r'(上海昊奕佳国际物流有限公司|上海璟易科国际物流有限公司)',
]

# 备注模式（用于 USD 检测）
REMARK_PATTERNS = [
    r'备注[：:](.*?)(?:\n|$)',
]

# 文件名中的非法字符（Windows）
INVALID_CHARS = r'<>:"/\|?*'

# 文件名分隔符
FILENAME_SEPARATOR = "-"
