"""发票识别与重命名工具 - GUI界面 v2.0"""
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import sys
import threading
from src.dependencies import ensure_dependencies
from src.pdf_extractor import extract_text_from_pdf
from src.invoice_parser import parse_invoice
from src.renamer import rename_file
from src.logger import InvoiceLogger
from src.config import LOG_FILE


class InvoiceRenamerGUI:
    """发票识别与重命名工具的GUI界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("发票识别与重命名工具 v2.0")
        self.root.geometry("700x580")
        self.root.resizable(True, True)

        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # 确保依赖已安装
        self.check_dependencies()

        self.setup_ui()
        self.setup_shortcuts()

        # 添加启动日志
        self.log_message("程序启动成功！准备就绪。", "info")

    def check_dependencies(self):
        """检查依赖是否已安装"""
        if not ensure_dependencies():
            messagebox.showerror(
                "错误",
                "依赖安装失败！\n请手动运行: pip install -r requirements.txt"
            )
            self.root.destroy()
            sys.exit(1)

    def setup_shortcuts(self):
        """设置快捷键"""
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-l>', lambda e: self.clear_log())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<Return>', lambda e: self.start_processing())

    def setup_ui(self):
        """设置GUI界面"""
        # ========== 顶部标题栏 ==========
        header_frame = tk.Frame(self.root, bg="#4A90E2", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="📄 发票识别与重命名工具",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg="#4A90E2",
            fg="white"
        )
        title_label.pack(pady=12)

        # ========== 主要内容区域 ==========
        main_frame = tk.Frame(self.root, bg="#FFFFFF", padx=25, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ========== 文件夹选择区域 ==========
        folder_frame = tk.Frame(main_frame, bg="#FFFFFF")
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            folder_frame,
            text="📁 选择包含PDF发票的文件夹：",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        ).pack(anchor=tk.W)

        input_frame = tk.Frame(folder_frame, bg="#FFFFFF")
        input_frame.pack(fill=tk.X, pady=8)

        self.folder_path = tk.StringVar()
        folder_entry = tk.Entry(
            input_frame,
            textvariable=self.folder_path,
            font=("Microsoft YaHei UI", 10),
            bg="#F5F5F5",
            fg="#333333",
            relief=tk.SOLID,
            borderwidth=1
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_button = tk.Button(
            input_frame,
            text="浏览...",
            command=self.browse_folder,
            font=("Microsoft YaHei UI", 10),
            width=10,
            bg="#4A90E2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5
        )
        browse_button.pack(side=tk.LEFT)

        # ========== 进度和统计区域 ==========
        stats_frame = tk.Frame(main_frame, bg="#FFFFFF")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(
            stats_frame,
            text="准备就绪",
            font=("Microsoft YaHei UI", 9),
            bg="#FFFFFF",
            fg="#666666"
        )
        self.status_label.pack(side=tk.LEFT)

        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Microsoft YaHei UI", 9),
            bg="#FFFFFF",
            fg="#999999"
        )
        self.stats_label.pack(side=tk.RIGHT)

        # ========== 日志输出区域 ==========
        log_frame = tk.Frame(main_frame, bg="#FFFFFF")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 日志标题
        log_header = tk.Frame(log_frame, bg="#FFFFFF")
        log_header.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            log_header,
            text="📋 处理日志：",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        ).pack(side=tk.LEFT)

        clear_small_btn = tk.Button(
            log_header,
            text="清空",
            command=self.clear_log,
            font=("Microsoft YaHei UI", 8),
            bg="#EEEEEE",
            fg="#666666",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=3
        )
        clear_small_btn.pack(side=tk.RIGHT)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            wrap=tk.WORD,
            height=16,
            bg="#F8F8F8",
            fg="#333333",
            insertbackground="#333333",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志文本标签
        self.log_text.tag_config("success", foreground="#00AA00")
        self.log_text.tag_config("error", foreground="#CC0000")
        self.log_text.tag_config("info", foreground="#0066CC")
        self.log_text.tag_config("warning", foreground="#FF9900")

        # ========== 按钮区域 ==========
        button_frame = tk.Frame(main_frame, bg="#FFFFFF")
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 主按钮
        self.process_button = tk.Button(
            button_frame,
            text="▶ 开始处理",
            command=self.start_processing,
            font=("Microsoft YaHei UI", 11, "bold"),
            width=15,
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))

        # 辅助按钮
        open_folder_button = tk.Button(
            button_frame,
            text="打开文件夹",
            command=self.open_folder,
            font=("Microsoft YaHei UI", 10),
            width=12,
            bg="#4A90E2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2"
        )
        open_folder_button.pack(side=tk.LEFT, padx=5)

        view_log_button = tk.Button(
            button_frame,
            text="查看日志文件",
            command=self.view_full_log,
            font=("Microsoft YaHei UI", 10),
            width=12,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2"
        )
        view_log_button.pack(side=tk.LEFT, padx=5)

        # ========== 底部信息栏 ==========
        footer_frame = tk.Frame(self.root, bg="#E0E0E0", height=35)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        footer_label = tk.Label(
            footer_frame,
            text="💡 快捷键: Ctrl+O 浏览文件夹 | Ctrl+L 清空日志 | F1 帮助 | Enter 开始处理",
            font=("Microsoft YaHei UI", 8),
            bg="#E0E0E0",
            fg="#666666"
        )
        footer_label.pack(pady=8)

    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory(title="选择包含PDF发票的文件夹")
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"已选择文件夹: {folder}", "info")

    def log_message(self, message, tag=None):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("日志已清空", "info")

    def open_folder(self):
        """打开当前选择的文件夹"""
        folder = self.folder_path.get()
        if folder and os.path.isdir(folder):
            os.startfile(folder)
            self.log_message(f"已打开文件夹: {folder}", "info")
        else:
            messagebox.showwarning("警告", "请先选择一个有效的文件夹！")

    def view_full_log(self):
        """查看完整的日志文件"""
        if os.path.exists(LOG_FILE):
            os.startfile(LOG_FILE)
        else:
            messagebox.showinfo("提示", "日志文件尚未生成")

    def show_help(self):
        """显示帮助对话框"""
        help_text = """
发票识别与重命名工具 - 使用帮助

【基本操作】
1. 选择包含PDF发票的文件夹
2. 点击"开始处理"按钮
3. 查看处理结果

【快捷键】
• Ctrl+O    - 浏览文件夹
• Ctrl+L    - 清空日志
• F1        - 显示此帮助
• Enter     - 开始处理

【支持的发票类型】
• 增值税专用发票
• 增值税普通发票

【注意事项】
• PDF文件需要有可提取的文本层
• 扫描件无法识别
• 确保发票中有"销售方名称"和"发票号码"字段

【技术支持】
如有问题请联系开发者
        """
        messagebox.showinfo("帮助", help_text)

    def process_invoice_file(self, pdf_path, logger):
        """处理单个发票文件"""
        filename = os.path.basename(pdf_path)
        self.log_message(f"处理文件: {filename}", "info")

        # 1. 提取PDF文本
        text = extract_text_from_pdf(pdf_path)
        if text is None:
            error_msg = "  [XX] 无法读取PDF文件"
            self.log_message(error_msg, "error")
            logger.log_failure(filename, "无法读取PDF")
            return False

        # 2. 解析发票字段
        invoice_info = parse_invoice(text)
        if invoice_info is None:
            error_msg = "  [XX] 未找到销售方或发票号码"
            self.log_message(error_msg, "error")
            logger.log_failure(filename, "未找到销售方或发票号码")
            return False

        # 3. 重命名文件（使用新参数格式）
        success, result = rename_file(
            pdf_path,
            invoice_info.get("buyer_alias"),
            invoice_info["seller"],
            invoice_info["invoice_no"],
            invoice_info.get("date"),
            invoice_info["is_usd"]
        )

        if success:
            success_msg = f"  [OK] 成功重命名为: {os.path.basename(result)}"
            self.log_message(success_msg, "success")
            logger.log_success(filename, os.path.basename(result))
            return True
        else:
            error_msg = f"  [XX] 重命名失败: {result}"
            self.log_message(error_msg, "error")
            logger.log_failure(filename, result)
            return False

    def start_processing(self):
        """开始处理"""
        input_dir = self.folder_path.get()

        # 验证输入
        if not input_dir:
            messagebox.showwarning("警告", "请先选择一个文件夹！")
            return

        if not os.path.isdir(input_dir):
            messagebox.showerror("错误", f"文件夹不存在：{input_dir}")
            return

        # 禁用按钮，防止重复点击
        self.process_button.config(state=tk.DISABLED, text="⏳ 处理中...")
        self.log_message("=" * 55, "info")

        # 在新线程中处理，避免界面卡顿
        thread = threading.Thread(target=self.process_files, args=(input_dir,))
        thread.daemon = True
        thread.start()

    def process_files(self, input_dir):
        """处理文件（在子线程中运行）"""
        try:
            # 初始化日志记录器
            logger = InvoiceLogger(LOG_FILE)

            # 查找所有PDF文件
            pdf_files = [
                os.path.join(input_dir, f)
                for f in os.listdir(input_dir)
                if f.lower().endswith('.pdf')
            ]

            if not pdf_files:
                self.root.after(0, lambda: self.log_message("没有找到PDF文件", "warning"))
                self.root.after(0, lambda: messagebox.showinfo("提示", f"在 {input_dir} 中没有找到PDF文件"))
                self.root.after(0, lambda: self.process_button.config(state=tk.NORMAL, text="▶ 开始处理"))
                return

            self.root.after(0, lambda: self.status_label.config(text=f"找到 {len(pdf_files)} 个PDF文件"))
            self.root.after(0, lambda: self.log_message(f"开始处理 {len(pdf_files)} 个PDF文件\n", "info"))

            # 处理每个PDF文件
            success_count = 0
            for i, pdf_path in enumerate(pdf_files, 1):
                self.root.after(0, lambda i=i, total=len(pdf_files): (
                    self.status_label.config(text=f"正在处理: {i}/{total}"),
                    self.stats_label.config(text=f"{i}/{total}")
                ))
                if self.process_invoice_file(pdf_path, logger):
                    success_count += 1

            # 完成
            self.root.after(0, lambda: self.log_message("=" * 55, "info"))
            self.root.after(0, lambda: self.log_message(f"\n处理完成！成功: {success_count}, 失败: {len(pdf_files) - success_count}", "success"))

            # 保存日志
            logger.save_to_file()
            logger.print_summary()

            self.root.after(0, lambda: self.status_label.config(
                text=f"完成！成功: {success_count}, 失败: {len(pdf_files) - success_count}"
            ))
            self.root.after(0, lambda: self.stats_label.config(text=""))

            # 显示完成对话框并询问是否打开文件夹
            def show_complete_dialog():
                result = messagebox.askyesno(
                    "处理完成",
                    f"处理完成！\n\n✓ 成功: {success_count} 个\n✗ 失败: {len(pdf_files) - success_count} 个\n\n是否打开文件夹查看结果？"
                )
                if result:
                    self.open_folder()

            self.root.after(0, show_complete_dialog)

        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self.log_message(error_msg, "error"))
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))

        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.process_button.config(state=tk.NORMAL, text="▶ 开始处理"))


def main():
    """主函数"""
    root = tk.Tk()
    app = InvoiceRenamerGUI(root)

    # 设置窗口关闭行为
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()
