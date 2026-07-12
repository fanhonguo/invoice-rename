"""发票识别与重命名工具 - 主程序"""
import os
import sys
import argparse
from src.dependencies import ensure_dependencies
from src.pdf_extractor import extract_text_from_pdf
from src.invoice_parser import parse_invoice
from src.renamer import rename_file
from src.logger import InvoiceLogger
from src.config import INPUT_DIR, LOG_FILE


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
        invoice_info.get("buyer_alias"),
        invoice_info["seller"],
        invoice_info["invoice_no"],
        invoice_info["is_usd"]
    )

    if success:
        logger.log_success(filename, os.path.basename(result))
        return True
    else:
        logger.log_failure(filename, result)
        return False


def main() -> None:
    """主函数"""
    """主函数"""
    # 首先确保所有依赖已安装
    if not ensure_dependencies():
        print("警告: 某些依赖未能成功安装，程序可能无法正常运行")
        print("建议手动运行: pip install -r requirements.txt")
        sys.exit(1)

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
