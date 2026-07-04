# 发票识别与重命名工具 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个Python工具，自动识别PDF发票中的销售方名称和发票号码，并重命名文件。

**Architecture:** 模块化设计，分为PDF文本提取、发票字段解析、文件重命名和日志记录四个模块。使用pdfplumber提取PDF文本，正则表达式匹配固定标签提取字段。

**Tech Stack:** Python 3.x, pdfplumber

---

## 文件结构

```
invoice-renamer/
├── main.py              # 主程序入口
├── pdf_extractor.py     # PDF文本提取
├── invoice_parser.py    # 发票字段解析
├── renamer.py           # 重命名逻辑
├── logger.py            # 日志记录
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
└── tests/               # 测试目录
    ├── test_pdf_extractor.py
    ├── test_invoice_parser.py
    └── test_renamer.py
```

---

## Task 1: 创建项目基础文件

**Files:**
- Create: `requirements.txt`
- Create: `config.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
pdfplumber==0.10.3
```

- [ ] **Step 2: 创建 config.py**

```python
"""配置文件"""

# 输入目录（默认为当前目录）
INPUT_DIR = "."

# 日志文件路径
LOG_FILE = "invoice_renamer.log"

# 正则表达式模式（用于匹配发票字段）
PATTERNS = [
    r'销售方：(.*?)发票号码：(.*?)',
    r'销售方:(.*?)发票号码:(.*?)'
]

# 文件名中的非法字符（Windows）
INVALID_CHARS = '<>:"/\|?*'
```

- [ ] **Step 3: 提交**

```bash
git add requirements.txt config.py
git commit -m "feat: add project config and dependencies"
```

---

## Task 2: 实现PDF文本提取模块

**Files:**
- Create: `pdf_extractor.py`
- Create: `tests/test_pdf_extractor.py`

- [ ] **Step 1: 写测试（先写失败的测试）**

创建 `tests/test_pdf_extractor.py`:

```python
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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_pdf_extractor.py -v
```
预期: FAIL - "No module named 'pdf_extractor'"

- [ ] **Step 3: 安装依赖**

```bash
pip install pdfplumber
```

- [ ] **Step 4: 实现pdf_extractor.py**

```python
"""PDF文本提取模块"""
import pdfplumber
from typing import Optional

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    从PDF文件中提取全部文本内容

    Args:
        pdf_path: PDF文件路径

    Returns:
        提取的文本内容，如果失败返回None
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts) if text_parts else None
    except Exception as e:
        print(f"读取PDF失败 {pdf_path}: {e}")
        return None
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/test_pdf_extractor.py -v
```
预期: PASS（如果有测试PDF）或 SKIP（如果没有）

- [ ] **Step 6: 提交**

```bash
git add pdf_extractor.py tests/test_pdf_extractor.py
git commit -m "feat: add PDF text extraction module"
```

---

## Task 3: 实现发票字段解析模块

**Files:**
- Create: `invoice_parser.py`
- Create: `tests/test_invoice_parser.py`

- [ ] **Step 1: 写测试**

创建 `tests/test_invoice_parser.py`:

```python
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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_invoice_parser.py -v
```
预期: FAIL - "No module named 'invoice_parser'"

- [ ] **Step 3: 实现invoice_parser.py**

```python
"""发票字段解析模块"""
import re
from typing import Optional, Dict
from config import PATTERNS

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
    # 去除首尾空格，替换换行符为空格
    value = value.strip()
    value = re.sub(r'[\r\n]+', ' ', value)
    # 去除多余空格
    value = re.sub(r'\s+', ' ', value)
    return value

def parse_invoice(text: str) -> Optional[Dict[str, str]]:
    """
    从文本中提取销售方名称和发票号码

    Args:
        text: PDF提取的文本内容

    Returns:
        包含seller和invoice_no的字典，如果提取失败返回None
    """
    if not text:
        return None

    for pattern in PATTERNS:
        match = re.search(pattern, text)
        if match:
            seller = clean_value(match.group(1))
            invoice_no = clean_value(match.group(2))

            # 验证两个字段都不为空
            if seller and invoice_no:
                return {
                    "seller": seller,
                    "invoice_no": invoice_no
                }

    return None
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_invoice_parser.py -v
```
预期: PASS

- [ ] **Step 5: 提交**

```bash
git add invoice_parser.py tests/test_invoice_parser.py
git commit -m "feat: add invoice field parser module"
```

---

## Task 4: 实现文件名清理功能

**Files:**
- Create: `renamer.py`
- Create: `tests/test_renamer.py`

- [ ] **Step 1: 写测试**

创建 `tests/test_renamer.py`:

```python
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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_renamer.py -v
```
预期: FAIL - "No module named 'renamer'"

- [ ] **Step 3: 实现renamer.py（部分）**

```python
"""文件重命名模块"""
import os
import re
from typing import Optional
from config import INVALID_CHARS

def clean_filename(name: str) -> str:
    """
    清理文件名中的非法字符

    Args:
        name: 原始名称

    Returns:
        清理后的名称
    """
    # 移除Windows非法字符
    for char in INVALID_CHARS:
        name = name.replace(char, '')
    return name

def construct_new_name(seller: str, invoice_no: str) -> str:
    """
    构造新文件名

    Args:
        seller: 销售方名称
        invoice_no: 发票号码

    Returns:
        新文件名（格式：销售方名称 发票号码.pdf）
    """
    clean_seller = clean_filename(seller)
    clean_invoice = clean_filename(invoice_no)
    return f"{clean_seller} {clean_invoice}.pdf"

def rename_file(original_path: str, seller: str, invoice_no: str) -> tuple[bool, str]:
    """
    重命名文件

    Args:
        original_path: 原文件完整路径
        seller: 销售方名称
        invoice_no: 发票号码

    Returns:
        (成功状态, 新文件路径或错误信息)
    """
    try:
        # 获取目录和原文件名
        directory = os.path.dirname(original_path)
        new_name = construct_new_name(seller, invoice_no)
        new_path = os.path.join(directory, new_name)

        # 检查目标文件是否已存在
        if os.path.exists(new_path):
            return False, "目标文件已存在"

        # 执行重命名
        os.rename(original_path, new_path)
        return True, new_path

    except Exception as e:
        return False, f"重命名失败: {str(e)}"
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_renamer.py -v
```
预期: PASS

- [ ] **Step 5: 提交**

```bash
git add renamer.py tests/test_renamer.py
git commit -m "feat: add file renaming module"
```

---

## Task 5: 实现日志模块

**Files:**
- Create: `logger.py`

- [ ] **Step 1: 实现logger.py**

```python
"""日志记录模块"""
import os
from datetime import datetime
from typing import List

class InvoiceLogger:
    """发票处理日志记录器"""

    def __init__(self, log_file: str = "invoice_renamer.log"):
        """
        初始化日志记录器

        Args:
            log_file: 日志文件路径
        """
        self.log_file = log_file
        self.success_count = 0
        self.failure_count = 0
        self.entries: List[dict] = []

    def log_success(self, original_name: str, new_name: str):
        """
        记录成功日志

        Args:
            original_name: 原文件名
            new_name: 新文件名
        """
        self.success_count += 1
        entry = {
            "status": "SUCCESS",
            "original": original_name,
            "new": new_name,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.entries.append(entry)
        print(f"[SUCCESS] {original_name} -> {new_name}")

    def log_failure(self, original_name: str, reason: str):
        """
        记录失败日志

        Args:
            original_name: 原文件名
            reason: 失败原因
        """
        self.failure_count += 1
        entry = {
            "status": "SKIP",
            "original": original_name,
            "reason": reason,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.entries.append(entry)
        print(f"[SKIP] {original_name} - {reason}")

    def save_to_file(self):
        """将日志保存到文件"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("发票重命名日志\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for entry in self.entries:
                if entry["status"] == "SUCCESS":
                    f.write(f"[SUCCESS] {entry['original']} -> {entry['new']}\n")
                else:
                    f.write(f"[SKIP] {entry['original']} - {entry['reason']}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write(f"总计: {self.success_count + self.failure_count} 个文件\n")
            f.write(f"成功: {self.success_count} 个\n")
            f.write(f"跳过: {self.failure_count} 个\n")
            f.write("=" * 60 + "\n")

    def print_summary(self):
        """打印汇总信息"""
        total = self.success_count + self.failure_count
        print("\n" + "=" * 60)
        print(f"处理完成！总计: {total} 个文件")
        print(f"成功: {self.success_count} 个 | 跳过: {self.failure_count} 个")
        print(f"日志已保存到: {self.log_file}")
        print("=" * 60)
```

- [ ] **Step 2: 创建测试验证logger**

创建 `tests/test_logger.py`:

```python
"""测试日志模块"""
import os
from logger import InvoiceLogger

def test_logger():
    """测试日志记录器"""
    logger = InvoiceLogger("test.log")

    logger.log_success("old.pdf", "new.pdf")
    logger.log_failure("fail.pdf", "无法读取")

    assert logger.success_count == 1
    assert logger.failure_count == 1
    assert len(logger.entries) == 2

    logger.save_to_file()
    assert os.path.exists("test.log")

    # 清理
    os.remove("test.log")
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_logger.py -v
```
预期: PASS

- [ ] **Step 4: 提交**

```bash
git add logger.py tests/test_logger.py
git commit -m "feat: add logging module"
```

---

## Task 6: 实现主程序

**Files:**
- Create: `main.py`

- [ ] **Step 1: 实现main.py**

```python
"""发票识别与重命名工具 - 主程序"""
import os
import sys
import argparse
from pdf_extractor import extract_text_from_pdf
from invoice_parser import parse_invoice
from renamer import rename_file
from logger import InvoiceLogger
from config import INPUT_DIR, LOG_FILE

def process_invoice_file(pdf_path: str, logger: InvoiceLogger) -> bool:
    """
    处理单个发票文件

    Args:
        pdf_path: PDF文件路径
        logger: 日志记录器

    Returns:
        处理是否成功
    """
    filename = os.path.basename(pdf_path)

    # 1. 提取PDF文本
    text = extract_text_from_pdf(pdf_path)
    if text is None:
        logger.log_failure(filename, "无法读取PDF")
        return False

    # 2. 解析发票字段
    invoice_info = parse_invoice(text)
    if invoice_info is None:
        logger.log_failure(filename, "未找到销售方或发票号码")
        return False

    # 3. 重命名文件
    success, result = rename_file(
        pdf_path,
        invoice_info["seller"],
        invoice_info["invoice_no"]
    )

    if success:
        logger.log_success(filename, os.path.basename(result))
        return True
    else:
        logger.log_failure(filename, result)
        return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="发票识别与重命名工具")
    parser.add_argument(
        "--path",
        default=INPUT_DIR,
        help="包含PDF发票的目录路径（默认当前目录）"
    )
    args = parser.parse_args()

    input_dir = args.path

    # 检查目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误: 目录不存在 - {input_dir}")
        sys.exit(1)

    # 初始化日志记录器
    logger = InvoiceLogger(LOG_FILE)

    # 查找所有PDF文件
    pdf_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith('.pdf')
    ]

    if not pdf_files:
        print(f"在 {input_dir} 中没有找到PDF文件")
        sys.exit(0)

    print(f"找到 {len(pdf_files)} 个PDF文件")
    print("开始处理...\n")

    # 处理每个PDF文件
    for pdf_path in pdf_files:
        process_invoice_file(pdf_path, logger)

    # 保存日志并打印汇总
    logger.save_to_file()
    logger.print_summary()

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试主程序（使用现有的测试PDF）**

```bash
# 先查看当前目录的PDF文件
ls -la *.pdf

# 运行程序（处理当前目录）
python main.py

# 或者处理指定目录
# python main.py --path /path/to/invoices
```

预期: 程序识别出PDF文件并尝试重命名

- [ ] **Step 3: 提交**

```bash
git add main.py
git commit -m "feat: add main program"
```

---

## Task 7: 创建README文档

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建README.md**

```markdown
# 发票识别与重命名工具

自动识别PDF发票中的销售方名称和发票号码，并将文件重命名为"销售方名称 发票号码.pdf"的格式。

## 功能特点

- 自动遍历文件夹中的所有PDF文件
- 从电子PDF中提取文本信息
- 通过固定标签识别销售方和发票号码
- 自动重命名文件
- 记录处理日志

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 使用方法

```bash
# 处理当前目录的PDF文件
python main.py

# 处理指定目录的PDF文件
python main.py --path /path/to/invoices
```

## 文件命名规则

- 格式: `销售方名称 发票号码.pdf`
- 发票号码原样保留（包括字母、符号）
- 文件名中的非法字符会被自动清理

## 日志

程序会生成 `invoice_renamer.log` 文件，记录每个文件的处理结果。

## 注意事项

- 适用于电子PDF（可直接选择文字的PDF）
- 发票需要有固定的"销售方："和"发票号码："标签
- 如果识别失败，文件不会被修改
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Task 8: 最终验证

**Files:**
- Test: 所有文件

- [ ] **Step 1: 运行所有测试**

```bash
pytest tests/ -v
```
预期: 所有测试通过

- [ ] **Step 2: 用实际PDF文件测试**

```bash
# 在包含测试PDF的目录运行
python main.py
```
预期: PDF文件被正确重命名

- [ ] **Step 3: 检查日志文件**

```bash
cat invoice_renamer.log
```
预期: 日志正确记录处理结果

- [ ] **Step 4: 最终提交**

```bash
git add .
git commit -m "chore: final verification and cleanup"
```
