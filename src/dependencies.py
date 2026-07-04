"""依赖管理模块 - 自动检查和安装项目依赖"""
import sys
import subprocess
from typing import List, Tuple


# 项目核心依赖（会自动安装/更新）
CORE_REQUIREMENTS = [
    "pdfplumber>=0.10.0",
]


def check_package_installed(package_name: str) -> bool:
    """
    检查包是否已安装

    Args:
        package_name: 包名（不含版本号）

    Returns:
        是否已安装
    """
    try:
        # 提取包名（去除版本号部分）
        base_name = package_name.split(">")[0].split("=")[0].split("<")[0].strip()
        __import__(base_name)
        return True
    except ImportError:
        return False


def install_package(package_spec: str) -> Tuple[bool, str]:
    """
    安装指定的包

    Args:
        package_spec: 包规格（含版本号，如 "pdfplumber>=0.10.0"）

    Returns:
        (是否成功, 消息)
    """
    try:
        # 使用当前Python环境的pip来安装
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_spec, "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True, f"成功安装 {package_spec}"
    except subprocess.CalledProcessError as e:
        return False, f"安装失败 {package_spec}: {e}"
    except Exception as e:
        return False, f"安装出错 {package_spec}: {e}"


def ensure_dependencies() -> bool:
    """
    确保所有核心依赖已安装

    启动时自动检查并安装缺失的核心依赖。
    用户手动通过pip安装的其他依赖不受影响。

    Returns:
        所有依赖是否都已就绪
    """
    all_ready = True
    any_action = False

    print("检查依赖...")

    for requirement in CORE_REQUIREMENTS:
        # 提取包名用于检查
        package_name = requirement.split(">")[0].split("=")[0].split("<")[0].strip()

        if check_package_installed(package_name):
            # 包已安装，检查是否需要更新（可选）
            print(f"  [OK] {requirement} (已安装)")
        else:
            # 包未安装，自动安装
            print(f"  [--] {requirement} (未安装) -> 正在安装...")
            success, msg = install_package(requirement)
            if success:
                print(f"  [OK] {msg}")
                any_action = True
            else:
                print(f"  [XX] {msg}")
                all_ready = False

    if any_action:
        print("依赖安装完成！\n")

    return all_ready


def get_missing_dependencies() -> List[str]:
    """
    获取缺失的依赖列表

    Returns:
        缺失的包名列表
    """
    missing = []
    for requirement in CORE_REQUIREMENTS:
        package_name = requirement.split(">")[0].split("=")[0].split("<")[0].strip()
        if not check_package_installed(package_name):
            missing.append(requirement)
    return missing


if __name__ == "__main__":
    # 测试依赖检查
    print("测试依赖管理模块")
    print(f"核心依赖: {CORE_REQUIREMENTS}")
    print(f"缺失依赖: {get_missing_dependencies()}")
    print(f"确保依赖: {ensure_dependencies()}")
