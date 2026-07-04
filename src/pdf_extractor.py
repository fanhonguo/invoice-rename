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
