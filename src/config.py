"""配置文件"""

# 输入目录（默认为当前目录）
INPUT_DIR = "."

# 日志文件路径（放在logs目录）
import os
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "invoice_renamer.log")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 正则表达式模式（用于匹配发票字段）
# 增值税发票格式：发票号码在顶部，销售方名称在"销 名称："之后
PATTERNS = [
    # 模式1: 匹配PDF提取时常见的格式 "销 名称：公司名"
    r'发票号码[：:]\s*(\d{15,21}).*?销\s名称[：:]\s*([^\s]{3,50}?\s*公司|[^\s]{3,50}?\s*物流|[^\s]{3,50}?\s*代理|[^\s]{3,50}?\s*科技)',
    # 模式2: 匹配更宽松的格式
    r'发票号码[：:]\s*(\d{15,21}).*?销\s名称[：:]\s*([^\r\n]{3,50}?)\s*信',
    # 模式3: 最宽松的模式，找"销 名称："后的任何文本直到行尾或下一个关键字
    r'发票号码[：:]\s*(\d{15,21}).*?销\s名称[：:]\s*([^\r\n]+?)(?:\s*$|\r|\n)',
]

# 文件名中的非法字符（Windows）
INVALID_CHARS = r'<>:"/\|?*'
