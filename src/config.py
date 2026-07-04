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

# 销售方名称模式（保留原有模式，重命名为更清晰的名称）
SELLER_PATTERNS = [
    r'发票号码[：:]\s*(\d{15,21}).*?销\s名称[：:]\s*([^\s]{3,50}?\s*公司|[^\s]{3,50}?\s*物流|[^\s]{3,50}?\s*代理|[^\s]{3,50}?\s*科技)',
    r'发票号码[：:]\s*(\d{15,21}).*?销\s名称[：:]\s*([^\r\n]{3,50}?)\s*信',
    r'发票号码[：:]\s*(\d{15,21}).*?销\s名称[：:]\s*([^\r\n]+?)(?:\s*$|\r|\n)',
]

# 购买方名称模式
BUYER_PATTERNS = [
    r'购买方名称[：:](.+?)(?:\n|$)',
]

# 发票号码模式（用于从混合文本中提取）
INVOICE_NO_PATTERNS = [
    r'发票号码[：:]\s*(\d{15,21})',
]

# 备注模式（用于 USD 检测）
REMARK_PATTERNS = [
    r'备注[：:](.*?)(?:\n|$)',
]

# 日期模式
DATE_PATTERNS = [
    r'开票日期[：:](\d{4})-(\d{1,2})-(\d{1,2})',
    r'开票日期[：:](\d{4})年(\d{1,2})月(\d{1,2})日',
    r'开票日期[：:](\d{4})/(\d{1,2})/(\d{1,2})',
    r'(\d{4})-(\d{1,2})-(\d{1,2})',
]

# 文件名中的非法字符（Windows）
INVALID_CHARS = r'<>:"/\|?*'

# 文件名分隔符
FILENAME_SEPARATOR = "-"
