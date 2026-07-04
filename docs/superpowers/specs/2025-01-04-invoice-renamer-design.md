# 发票识别与重命名工具 - 设计文档

**日期**: 2025-01-04
**作者**: Claude
**状态**: 设计阶段

---

## 项目概述

创建一个工具，自动识别PDF发票中的销售方名称和发票号码，并将文件重命名为"销售方名称 发票号码.pdf"的格式。

### 关键需求

- 遍历指定文件夹中的所有PDF文件
- 从PDF中提取销售方名称和发票号码
- 重命名文件为"销售方名称 发票号码.pdf"
- 提取失败时跳过文件并记录日志
- 发票号码原样保留（包括字母、符号）
- 销售方名称不截断

---

## 技术选型

**方案选择**: 纯Python方案

- 使用 `pdfplumber` 库提取PDF文本内容
- 使用正则表达式匹配固定标签"销售方："和"发票号码："
- 原因：轻量、免费、适合电子PDF场景

---

## 系统架构

### 模块划分

```
invoice-renamer/
├── main.py              # 主程序入口
├── pdf_extractor.py     # PDF文本提取
├── invoice_parser.py    # 发票字段解析
├── renamer.py           # 重命名逻辑
├── logger.py            # 日志记录
├── config.py            # 配置文件
└── requirements.txt     # 依赖列表
```

### 数据流程

```
PDF文件 → 提取文本 → 正则匹配 → 提取字段 → 构造新文件名 → 重命名
                                              ↓
                                          记录日志
```

---

## 核心模块设计

### 1. PDF文本提取模块 (pdf_extractor.py)

**职责**: 从PDF文件中提取全部文本内容

**接口**:
```python
def extract_text_from_pdf(pdf_path: str) -> str | None
```

**实现细节**:
- 使用 pdfplumber 打开PDF
- 遍历所有页面提取文本
- 处理可能的异常（损坏的文件、权限问题）
- 返回None表示提取失败

---

### 2. 发票字段解析模块 (invoice_parser.py)

**职责**: 从文本中提取销售方名称和发票号码

**接口**:
```python
def parse_invoice(text: str) -> dict | None
# 返回: {"seller": str, "invoice_no": str} 或 None
```

**实现细节**:
- 使用正则表达式匹配模式
- 模式1: `销售方：(.*?)发票号码：(.*?)`
- 模式2: `销售方:(.*?)发票号码:(.*?)`（无冒号空格）
- 清理提取结果（去除多余空格、换行符）
- 验证提取的字段不为空

---

### 3. 重命名模块 (renamer.py)

**职责**: 执行文件重命名

**接口**:
```python
def rename_file(original_path: str, seller: str, invoice_no: str) -> bool
```

**实现细节**:
- 构造新文件名: `{seller} {invoice_no}.pdf`
- 清理文件名中的非法字符（Windows: `<>:"/\|?*`）
- 检查目标文件是否已存在
- 执行重命名
- 返回成功/失败状态

---

### 4. 日志模块 (logger.py)

**职责**: 记录处理过程和结果

**接口**:
```python
def log_success(original_name: str, new_name: str)
def log_failure(original_name: str, reason: str)
def generate_report() -> str
```

**实现细节**:
- 记录到控制台和日志文件 `invoice_renamer.log`
- 成功日志: `[SUCCESS] 原文件名 -> 新文件名`
- 失败日志: `[SKIP] 原文件名 - 原因`
- 生成汇总报告

---

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| PDF读取失败 | 跳过文件，记录"无法读取PDF" |
| 找不到销售方 | 跳过文件，记录"未找到销售方" |
| 找不到发票号码 | 跳过文件，记录"未找到发票号码" |
| 文件名冲突 | 跳过文件，记录"目标文件已存在" |
| 文件名含非法字符 | 清理后重命名，记录日志 |

---

## 配置选项 (config.py)

```python
# 输入目录
INPUT_DIR = "./invoices"

# 日志文件路径
LOG_FILE = "./invoice_renamer.log"

# 正则表达式模式
PATTERNS = [
    r"销售方：(.*?)发票号码：(.*?)",
    r"销售方:(.*?)发票号码:(.*?)"
]
```

---

## 使用方式

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序（处理当前目录）
python main.py

# 运行程序（处理指定目录）
python main.py --path /path/to/invoices
```

---

## 依赖列表 (requirements.txt)

```
pdfplumber==0.10.3
```
