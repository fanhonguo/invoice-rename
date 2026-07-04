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

# 或直接运行主程序
python -m src.main --path /path/to/invoices
```

## 配置

编辑 `src/config.py` 可以自定义：

- **购买方简称映射表：** 添加更多购买方的简称规则
- **USD 检测关键词：** 自定义 USD 付款检测的关键词列表
- **文件名分隔符：** 修改文件名各部分之间的分隔符（默认为 `-`）

```python
# 示例：添加新的购买方简称
BUYER_ALIAS_MAP = {
    "上海昊奕佳国际物流有限公司": "昊奕佳",
    "上海璟易科国际物流有限公司": "璟易科",
    "你的公司名称": "你的简称",
}

# 示例：添加 USD 检测关键词
USD_KEYWORDS = [
    "汇率",
    "$",
    "仅限",
    "只接受",
    # ... 更多关键词
]
```

## 项目结构

```
发票识别与命名/
├── run.py                    # 启动脚本
├── requirements.txt          # 依赖列表
├── README.md                 # 项目说明
├── src/                      # 源代码目录
│   ├── config.py            # 配置文件
│   ├── main.py              # 命令行入口
│   ├── dependencies.py      # 依赖管理
│   ├── invoice_parser.py    # 发票解析
│   ├── pdf_extractor.py     # PDF 提取
│   ├── renamer.py           # 文件重命名
│   ├── logger.py            # 日志记录
│   └── gui.py               # GUI 界面
├── logs/                     # 日志目录
├── tests/                    # 测试文件
└── docs/                     # 文档
```

## 注意事项

- 适用于电子 PDF（可直接选择文字的 PDF）
- 发票需要有固定的标签格式
- 如果识别失败，文件不会被修改
- 目标文件已存在时会跳过该文件

## 日志

程序会生成 `logs/invoice_renamer.log` 文件，记录每个文件的处理结果。

## 运行测试

```bash
pytest tests/
```

## 系统要求

- Python 3.9+
- pdfplumber 库

## 许可证

MIT License
