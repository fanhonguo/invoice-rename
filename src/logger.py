"""日志记录模块"""
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
