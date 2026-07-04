# 发票识别与重命名工具

自动识别增值税发票信息并按规范重命名文件的工具。

## 功能特点

- 自动识别发票中的**销售方名称**和**发票号码**
- 批量处理文件夹中的所有PDF发票
- 支持增值税专用发票和普通发票
- 提供图形界面和命令行两种使用方式
- 一键打包为独立可执行文件

## 快速开始

### Windows用户（推荐）

1. 下载 `发票识别与重命名工具.exe`
2. 双击运行
3. 选择文件夹，点击"开始处理"

### Python用户

```bash
# 安装依赖
pip install -r requirements.txt

# 运行GUI
python run.py

# 或直接运行
python src/gui.py
```

## 项目结构

```
发票识别与命名/
├── 发票识别与重命名工具.exe  # 可执行文件（双击运行）
├── run.py                    # Python启动脚本
├── requirements.txt          # 依赖列表
├── README.md                 # 项目说明
├── .gitignore               # Git忽略文件
├── src/                     # 源代码目录
│   ├── gui.py              # GUI界面
│   ├── main.py             # 命令行入口
│   ├── dependencies.py     # 依赖管理
│   ├── invoice_parser.py   # 发票解析
│   ├── pdf_extractor.py    # PDF提取
│   ├── renamer.py          # 文件重命名
│   ├── logger.py           # 日志记录
│   └── config.py           # 配置文件
├── logs/                    # 日志目录
│   └── invoice_renamer.log  # 运行日志
├── tests/                   # 测试文件
├── docs/                    # 文档
│   ├── 分发说明.md
│   └── 更新文档.md
└── dist/                    # 打包输出（不提交到Git）
```

## 文件命名规则

处理后文件格式：`销售方名称 发票号码.pdf`

**示例：**
- 原文件：`丹纳 3781885021.pdf`
- 重命名后：`上海丹纳国际物流有限公司 26312000003781885021.pdf`

## 系统要求

- Windows 7/8/10/11
- Python 3.9+ （源代码运行）
- pdfplumber 库

## 开发

### 打包为exe

```bash
# 方式1: 打包普通版GUI
pyinstaller --onefile --windowed --name="发票识别与重命名工具" src/gui.py

# 方式2: 打包增强版GUI
pyinstaller --onefile --windowed --name="发票识别与重命名工具增强版" src/gui_enhanced.py
```

### 运行测试

```bash
pytest tests/
```

## Git提交

提交到Git时只需要以下文件：
```
src/           # 所有源代码
tests/         # 测试文件
docs/          # 文档
run.py         # 启动脚本
requirements.txt
README.md
.gitignore
logs/.gitkeep  # 保留空的logs目录
```

不需要提交：
```
.venv/         # 虚拟环境
dist/          # 打包输出
build/         # 打包临时文件
*.log          # 日志文件
*.pdf          # 示例文件
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
