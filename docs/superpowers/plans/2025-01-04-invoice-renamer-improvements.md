# 发票重命名工具改进 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改进发票重命名工具，支持购买方简称、连字符分隔、USD 后缀检测和日期格式统一

**Architecture:** 扩展现有模块，在 config.py 中添加映射表和关键词配置，在 invoice_parser.py 中添加购买方、日期和备注提取，在 renamer.py 中修改文件名构造逻辑

**Tech Stack:** Python 3.x, pdfplumber, pytest

---

## 新的文件名格式

```
{购买方简称}-{销售方名称}-{发票号码}-{日期}-USD.pdf
```

**示例：**
- 有 USD: `昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04-USD.pdf`
- 无 USD: `昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf`

---

## Task 1: 更新配置文件 - 添加映射表和关键词

**Files:**
- Modify: `src/config.py`

- [ ] **Step 1: 先查看当前 config.py 的内容**

```bash
cat src/config.py
```

- [ ] **Step 2: 更新 config.py，添加购买方简称映射和 USD 关键词**

```python
"""配置文件 - 发票重命名工具"""

from typing import Dict, List

# 输入目录（默认为当前目录）
INPUT_DIR = "."

# 日志文件路径
LOG_FILE = "invoice_renamer.log"

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

# 正则表达式模式（用于匹配发票字段）
# 顺序很重要：更精确的模式放在前面
SELLER_PATTERNS = [
    r'销售方名称：(.*?)发票号码：',
    r'销售方：(.*?)发票号码：',
    r'销售方名称:(.*?)发票号码:',
    r'销售方:(.*?)发票号码:',
]

# 购买方名称模式
BUYER_PATTERNS = [
    r'购买方名称：(.+?)(?:\n|$)',
    r'购买方名称:(.+?)(?:\n|$)',
]

# 发票号码模式（用于从混合文本中提取）
INVOICE_NO_PATTERNS = [
    r'发票号码：(\d+)',
    r'发票号码:(\d+)',
]

# 备注模式（用于 USD 检测）
REMARK_PATTERNS = [
    r'备注：(.*?)(?:\n|$)',
    r'备注:(.*?)(?:\n|$)',
]

# 日期模式
DATE_PATTERNS = [
    r'开票日期：(\d{4})-(\d{1,2})-(\d{1,2})',
    r'开票日期：(\d{4})年(\d{1,2})月(\d{1,2})日',
    r'开票日期：(\d{4})/(\d{1,2})/(\d{1,2})',
    r'(\d{4})-(\d{1,2})-(\d{1,2})',
]

# 文件名中的非法字符（Windows）
INVALID_CHARS = '<>:"/\|?*'

# 文件名分隔符
FILENAME_SEPARATOR = "-"
```

- [ ] **Step 3: 运行测试确保配置没有语法错误**

```bash
python -c "import src.config; print('Config loaded successfully')"
```

预期: 输出 "Config loaded successfully"

- [ ] **Step 4: 提交**

```bash
git add src/config.py
git commit -m "feat(config): add buyer alias map and USD keywords"
```

---

## Task 2: 扩展发票解析器 - 添加购买方、日期和备注提取

**Files:**
- Modify: `src/invoice_parser.py`
- Test: `tests/test_invoice_parser.py`

- [ ] **Step 1: 查看当前 invoice_parser.py 的内容**

```bash
cat src/invoice_parser.py
```

- [ ] **Step 2: 先为新增功能编写测试**

在 `tests/test_invoice_parser.py` 中添加：

```python
"""测试发票字段解析模块 - 新增功能测试"""
import pytest
from src.invoice_parser import (
    parse_invoice,
    extract_buyer_alias,
    extract_invoice_date,
    check_usd_payment,
    clean_value
)

def test_extract_buyer_alias_with_known_buyer():
    """测试已知购买方的简称提取"""
    text = "购买方名称：上海昊奕佳国际物流有限公司\n销售方名称：某某公司"
    alias = extract_buyer_alias(text)
    assert alias == "昊奕佳"

def test_extract_buyer_alias_with_unknown_buyer():
    """测试未知购买方返回 None"""
    text = "购买方名称：未知公司有限公司\n销售方名称：某某公司"
    alias = extract_buyer_alias(text)
    assert alias is None

def test_extract_buyer_alias_no_buyer_found():
    """测试没有购买方信息"""
    text = "销售方名称：某某公司"
    alias = extract_buyer_alias(text)
    assert alias is None

def test_extract_invoice_date_standard_format():
    """测试标准日期格式提取"""
    text = "开票日期：2025-01-04\n销售方名称：某某公司"
    date = extract_invoice_date(text)
    assert date == "2025-01-04"

def test_extract_invoice_date_chinese_format():
    """测试中文日期格式提取"""
    text = "开票日期：2025年1月4日\n销售方名称：某某公司"
    date = extract_invoice_date(text)
    assert date == "2025-01-04"

def test_extract_invoice_date_no_date_found():
    """测试没有日期信息"""
    text = "销售方名称：某某公司"
    date = extract_invoice_date(text)
    assert date is None

def test_check_usd_payment_with_dollar_sign():
    """测试包含美元符号"""
    text = "备注：汇率 $ 6.5"
    result = check_usd_payment(text)
    assert result is True

def test_check_usd_payment_with_keywords():
    """测试包含 USD 关键词"""
    text = "备注：仅接受美金付款"
    result = check_usd_payment(text)
    assert result is True

def test_check_usd_payment_no_keywords():
    """测试不包含 USD 关键词"""
    text = "备注：普通付款"
    result = check_usd_payment(text)
    assert result is False

def test_parse_invoice_extended():
    """测试扩展后的解析功能"""
    text = """
    购买方名称：上海昊奕佳国际物流有限公司
    销售方名称：美设国际物流集团股份有限公司
    发票号码：1657614422
    开票日期：2025-01-04
    备注：船名航次:ANL OTAGO 514S 汇率 6.5
    """
    result = parse_invoice(text)
    assert result is not None
    assert result["seller"] == "美设国际物流集团股份有限公司"
    assert result["invoice_no"] == "1657614422"
    assert result["buyer_alias"] == "昊奕佳"
    assert result["date"] == "2025-01-04"
    assert result["is_usd"] is True
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/test_invoice_parser.py -v
```

预期: FAIL - 函数未定义

- [ ] **Step 4: 实现 invoice_parser.py 的新功能**

```python
"""发票字段解析模块"""
import re
from typing import Optional, Dict
from src.config import (
    SELLER_PATTERNS,
    BUYER_PATTERNS,
    INVOICE_NO_PATTERNS,
    REMARK_PATTERNS,
    DATE_PATTERNS,
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
    value = value.strip()
    value = re.sub(r'[\r\n]+', ' ', value)
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


def extract_invoice_date(text: str) -> Optional[str]:
    """
    从文本中提取开票日期

    Args:
        text: PDF 提取的文本内容

    Returns:
        标准格式的日期字符串 (YYYY-MM-DD)，如果未找到返回 None
    """
    if not text:
        return None

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                year, month, day = groups
                # 标准化为 YYYY-MM-DD 格式
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

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


def parse_invoice(text: str) -> Optional[Dict[str, any]]:
    """
    从文本中提取发票所有字段

    Args:
        text: PDF 提取的文本内容

    Returns:
        包含以下字段的字典:
        - seller: 销售方名称
        - invoice_no: 发票号码
        - buyer_alias: 购买方简称 (可选)
        - date: 开票日期 (可选)
        - is_usd: 是否为 USD 付款
        如果提取失败返回 None
    """
    if not text:
        return None

    # 提取销售方名称和发票号码
    seller = None
    invoice_no = None

    for pattern in SELLER_PATTERNS:
        match = re.search(pattern, text)
        if match:
            seller = clean_value(match.group(1))
            # 尝试从同一行或后续行提取发票号码
            for invoice_pattern in INVOICE_NO_PATTERNS:
                invoice_match = re.search(invoice_pattern, text)
                if invoice_match:
                    invoice_no = clean_value(invoice_match.group(1))
                    break
            if seller and invoice_no:
                break

    if not seller or not invoice_no:
        return None

    # 提取可选字段
    buyer_alias = extract_buyer_alias(text)
    date = extract_invoice_date(text)
    is_usd = check_usd_payment(text)

    return {
        "seller": seller,
        "invoice_no": invoice_no,
        "buyer_alias": buyer_alias,
        "date": date,
        "is_usd": is_usd
    }
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/test_invoice_parser.py -v
```

预期: PASS

- [ ] **Step 6: 提交**

```bash
git add src/invoice_parser.py tests/test_invoice_parser.py
git commit -m "feat(parser): add buyer alias, date and USD detection"
```

---

## Task 3: 更新重命名模块 - 使用新的文件名格式

**Files:**
- Modify: `src/renamer.py`
- Test: `tests/test_renamer.py`

- [ ] **Step 1: 查看当前 renamer.py 的内容**

```bash
cat src/renamer.py
```

- [ ] **Step 2: 先为新格式编写测试**

更新 `tests/test_renamer.py`：

```python
"""测试重命名模块 - 新格式测试"""
import pytest
from src.renamer import clean_filename, construct_new_name

def test_clean_filename():
    """测试清理文件名中的非法字符"""
    assert clean_filename('测试<公司>') == '测试公司'
    assert clean_filename('A:B/C|D*E?F') == 'ABCDEF'
    assert clean_filename('正常公司123') == '正常公司123'
    # 保留连字符
    assert clean_filename('公司-A-公司') == '公司-A-公司'

def test_construct_new_name_full():
    """测试完整的新文件名格式"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        date="2025-01-04",
        is_usd=True
    )
    assert result == "昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04-USD.pdf"

def test_construct_new_name_without_usd():
    """测试不含 USD 的文件名"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        date="2025-01-04",
        is_usd=False
    )
    assert result == "昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf"

def test_construct_new_name_no_buyer_alias():
    """测试没有购买方简称的文件名"""
    result = construct_new_name(
        buyer_alias=None,
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        date="2025-01-04",
        is_usd=False
    )
    assert result == "美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf"

def test_construct_new_name_no_date():
    """测试没有日期的文件名"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设国际物流集团股份有限公司",
        invoice_no="1657614422",
        date=None,
        is_usd=True
    )
    assert result == "昊奕佳-美设国际物流集团股份有限公司-1657614422-USD.pdf"

def test_construct_new_name_minimal():
    """测试最小文件名（只有销售方和发票号）"""
    result = construct_new_name(
        buyer_alias=None,
        seller="美设公司",
        invoice_no="12345",
        date=None,
        is_usd=False
    )
    assert result == "美设公司-12345.pdf"

def test_construct_new_name_with_invalid_chars():
    """测试含非法字符的文件名清理"""
    result = construct_new_name(
        buyer_alias="昊奕佳",
        seller="美设<国际>物流",
        invoice_no="12345",
        date="2025-01-04",
        is_usd=False
    )
    assert result == "昊奕佳-美设国际物流-12345-2025-01-04.pdf"
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/test_renamer.py -v
```

预期: FAIL - 函数签名或行为不匹配

- [ ] **Step 4: 实现 renamer.py 的新功能**

```python
"""文件重命名模块"""
import os
from typing import Optional
from src.config import INVALID_CHARS, FILENAME_SEPARATOR


def clean_filename(name: str) -> str:
    """
    清理文件名中的非法字符

    Args:
        name: 原始名称

    Returns:
        清理后的名称
    """
    if not name:
        return ""
    # 移除 Windows 非法字符
    for char in INVALID_CHARS:
        name = name.replace(char, '')
    return name


def construct_new_name(
    buyer_alias: Optional[str],
    seller: str,
    invoice_no: str,
    date: Optional[str],
    is_usd: bool
) -> str:
    """
    构造新文件名

    Args:
        buyer_alias: 购买方简称（可选）
        seller: 销售方名称
        invoice_no: 发票号码
        date: 开票日期（可选，格式 YYYY-MM-DD）
        is_usd: 是否为 USD 付款

    Returns:
        新文件名
        格式: {购买方简称}-{销售方名称}-{发票号码}-{日期}-USD.pdf
             或 {购买方简称}-{销售方名称}-{发票号码}-{日期}.pdf
    """
    parts = []

    # 添加购买方简称（如果有）
    if buyer_alias:
        parts.append(clean_filename(buyer_alias))

    # 添加销售方名称
    parts.append(clean_filename(seller))

    # 添加发票号码
    parts.append(clean_filename(invoice_no))

    # 添加日期（如果有）
    if date:
        parts.append(clean_filename(date))

    # 添加 USD 后缀（如果需要）
    if is_usd:
        parts.append("USD")

    return FILENAME_SEPARATOR.join(parts) + ".pdf"


def rename_file(
    original_path: str,
    buyer_alias: Optional[str],
    seller: str,
    invoice_no: str,
    date: Optional[str],
    is_usd: bool
) -> tuple[bool, str]:
    """
    重命名文件

    Args:
        original_path: 原文件完整路径
        buyer_alias: 购买方简称（可选）
        seller: 销售方名称
        invoice_no: 发票号码
        date: 开票日期（可选）
        is_usd: 是否为 USD 付款

    Returns:
        (成功状态, 新文件路径或错误信息)
    """
    try:
        directory = os.path.dirname(original_path)
        new_name = construct_new_name(buyer_alias, seller, invoice_no, date, is_usd)
        new_path = os.path.join(directory, new_name)

        if os.path.exists(new_path):
            return False, "目标文件已存在"

        os.rename(original_path, new_path)
        return True, new_path

    except Exception as e:
        return False, f"重命名失败: {str(e)}"
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/test_renamer.py -v
```

预期: PASS

- [ ] **Step 6: 提交**

```bash
git add src/renamer.py tests/test_renamer.py
git commit -m "feat(renamer): update to new filename format with separator"
```

---

## Task 4: 更新主程序 - 传递新的参数

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: 查看当前 main.py 的内容**

```bash
cat src/main.py
```

- [ ] **Step 2: 更新 process_invoice_file 函数**

```python
"""发票识别与重命名工具 - 主程序"""
import os
import sys
import argparse
from src.pdf_extractor import extract_text_from_pdf
from src.invoice_parser import parse_invoice
from src.renamer import rename_file
from src.logger import InvoiceLogger
from src.config import INPUT_DIR, LOG_FILE


def process_invoice_file(pdf_path: str, logger: InvoiceLogger) -> bool:
    """
    处理单个发票文件

    Args:
        pdf_path: PDF 文件路径
        logger: 日志记录器

    Returns:
        处理是否成功
    """
    filename = os.path.basename(pdf_path)

    # 1. 提取 PDF 文本
    text = extract_text_from_pdf(pdf_path)
    if text is None:
        logger.log_failure(filename, "无法读取 PDF")
        return False

    # 2. 解析发票字段
    invoice_info = parse_invoice(text)
    if invoice_info is None:
        logger.log_failure(filename, "未找到销售方或发票号码")
        return False

    # 3. 重命名文件（使用新的参数格式）
    success, result = rename_file(
        pdf_path,
        invoice_info.get("buyer_alias"),
        invoice_info["seller"],
        invoice_info["invoice_no"],
        invoice_info.get("date"),
        invoice_info["is_usd"]
    )

    if success:
        logger.log_success(filename, os.path.basename(result))
        return True
    else:
        logger.log_failure(filename, result)
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="发票识别与重命名工具")
    parser.add_argument(
        "--path",
        default=INPUT_DIR,
        help="包含 PDF 发票的目录路径（默认当前目录）"
    )
    args = parser.parse_args()

    input_dir = args.path

    if not os.path.isdir(input_dir):
        print(f"错误: 目录不存在 - {input_dir}")
        sys.exit(1)

    logger = InvoiceLogger(LOG_FILE)

    pdf_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith('.pdf')
    ]

    if not pdf_files:
        print(f"在 {input_dir} 中没有找到 PDF 文件")
        sys.exit(0)

    print(f"找到 {len(pdf_files)} 个 PDF 文件")
    print("开始处理...\n")

    for pdf_path in pdf_files:
        process_invoice_file(pdf_path, logger)

    logger.save_to_file()
    logger.print_summary()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 测试主程序语法正确**

```bash
python -m py_compile src/main.py
```

预期: 无输出

- [ ] **Step 4: 提交**

```bash
git add src/main.py
git commit -m "feat(main): update to use new invoice parser fields"
```

---

## Task 5: 更新测试 - 确保所有测试通过

**Files:**
- Test: `tests/`

- [ ] **Step 1: 运行所有测试**

```bash
pytest tests/ -v
```

预期: PASS

- [ ] **Step 2: 如果有失败的测试，修复并重新运行**

```bash
pytest tests/ -v --tb=short
```

- [ ] **Step 3: 测试覆盖率检查**

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

- [ ] **Step 4: 提交测试更新（如有）**

```bash
git add tests/
git commit -m "test: update tests for new features"
```

---

## Task 6: 更新文档

**Files:**
- Modify: `README.md`
- Create: `docs/更新说明.md`

- [ ] **Step 1: 更新 README.md**

```markdown
# 发票识别与重命名工具

自动识别 PDF 发票中的关键信息，并将文件重命名为结构化格式。

## 功能特点

- 自动遍历文件夹中的所有 PDF 文件
- 从电子 PDF 中提取文本信息
- 识别销售方名称、发票号码、购买方简称、开票日期
- 自动检测 USD 付款标识
- 生成统一的文件名格式
- 记录处理日志

## 文件命名规则

**格式：** `{购买方简称}-{销售方名称}-{发票号码}-{日期}-USD.pdf`

**示例：**
- 有 USD 付款：`昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04-USD.pdf`
- 无 USD 付款：`昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf`
- 无购买方简称：`美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf`

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
# 处理当前目录的 PDF 文件
python run.py

# 处理指定目录的 PDF 文件
python run.py --path /path/to/invoices
```

## 配置

编辑 `src/config.py` 可以自定义：

- **购买方简称映射表：** 添加更多购买方的简称规则
- **USD 检测关键词：** 自定义 USD 付款检测的关键词列表
- **文件名分隔符：** 修改文件名各部分之间的分隔符（默认为 `-`）

## 注意事项

- 适用于电子 PDF（可直接选择文字的 PDF）
- 发票需要有固定的标签格式
- 如果识别失败，文件不会被修改
- 目标文件已存在时会跳过该文件

## 日志

程序会生成 `invoice_renamer.log` 文件，记录每个文件的处理结果。
```

- [ ] **Step 2: 创建更新说明文档**

```markdown
# 更新说明

## 2025-01-04 - 功能改进

### 新增功能

1. **购买方简称**
   - 在文件名中添加购买方简称作为第一项
   - 简称从配置文件中的映射表获取
   - 默认支持：昊奕佳（上海昊奕佳国际物流有限公司）、璟易科（上海璟易科国际物流有限公司）

2. **文件名格式统一**
   - 使用连字符 `-` 分隔各部分
   - 格式：`{购买方简称}-{销售方名称}-{发票号码}-{日期}-USD`
   - 去除了之前格式中的空格

3. **USD 付款标识**
   - 自动检测发票备注中的 USD 相关关键词
   - 检测到时在文件名末尾添加 `-USD` 后缀
   - 支持的关键词：汇率、$、仅限、只接受、美金付款、美元付款等

4. **日期格式统一**
   - 自动提取开票日期
   - 统一格式为 `YYYY-MM-DD`
   - 支持多种输入格式：`2025-01-04`、`2025年1月4日`、`2025/1/4`

### 文件名示例

| 场景 | 文件名示例 |
|------|-----------|
| 完整信息（含 USD） | `昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04-USD.pdf` |
| 完整信息（不含 USD） | `昊奕佳-美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf` |
| 无购买方简称 | `美设国际物流集团股份有限公司-1657614422-2025-01-04.pdf` |

### 配置说明

在 `src/config.py` 中可以配置：

- `BUYER_ALIAS_MAP`: 添加更多购买方简称映射
- `USD_KEYWORDS`: 自定义 USD 检测关键词
- `FILENAME_SEPARATOR`: 修改文件名分隔符（默认 `-`）

### 兼容性

- 向后兼容：旧的发票文件仍可正确识别
- 原有测试全部通过
```

- [ ] **Step 3: 提交文档更新**

```bash
git add README.md docs/更新说明.md
git commit -m "docs: update README and add changelog"
```

---

## Task 7: 最终验证

**Files:**
- Test: 完整系统

- [ ] **Step 1: 运行完整测试套件**

```bash
pytest tests/ -v --cov=src --cov-report=term
```

预期: 所有测试通过，覆盖率 > 80%

- [ ] **Step 2: 使用实际 PDF 文件测试**

```bash
# 在包含测试 PDF 的目录运行
python run.py --path /path/to/test/invoices
```

预期:
- PDF 文件被正确重命名
- 日志文件正确生成
- 控制台输出显示处理结果

- [ ] **Step 3: 检查生成的文件名**

```bash
ls -la /path/to/test/invoices/*.pdf
```

验证文件名符合新格式

- [ ] **Step 4: 检查日志内容**

```bash
cat invoice_renamer.log
```

验证日志正确记录所有处理结果

- [ ] **Step 5: 清理测试文件**

```bash
# 清理测试生成的日志
rm -f invoice_renamer.log
```

- [ ] **Step 6: 最终提交**

```bash
git status
git add .
git commit -m "chore: final verification complete"
```

---

## Task 8: 创建 Git 标签（可选）

**Files:**
- Git

- [ ] **Step 1: 创建版本标签**

```bash
git tag -a v2.0.0 -m "改进版本：添加购买方简称、USD 检测和统一日期格式"
```

- [ ] **Step 2: 查看标签**

```bash
git tag -n
```

- [ ] **Step 3: 推送标签到远程（如需要）**

```bash
git push origin v2.0.0
```

---

## 计划完成检查清单

- [ ] 配置文件更新（购买方映射、USD 关键词）
- [ ] 发票解析器扩展（购买方、日期、备注）
- [ ] 重命名模块更新（新文件名格式）
- [ ] 主程序更新（传递新参数）
- [ ] 所有测试通过
- [ ] 文档更新
- [ ] 实际 PDF 验证
- [ ] 日志验证
