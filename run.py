"""发票识别与重命名工具 - 启动入口"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行GUI
from gui import main

if __name__ == "__main__":
    main()
