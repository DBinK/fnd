from pathlib import Path
from fnd import find_files
from fnd.core import FndConfig


def custom_size_filter(file_path: str) -> bool:
    """
    自定义过滤器：只保留大于 1KB 的文件
    """
    try:
        return Path(file_path).stat().st_size > 1024  # 大于 1KB
    except OSError:
        # 如果无法访问文件，返回 False
        return False


def custom_extension_filter(file_path: str) -> bool:
    """
    自定义过滤器：排除常见的临时文件和隐藏文件
    """
    path = Path(file_path)
    
    # 检查是否为隐藏文件或临时文件
    if path.name.startswith('.') or path.suffix in ['.tmp', '.temp', '.cache']:
        return False
    return True


def custom_date_filter(file_path: str) -> bool:
    """
    自定义过滤器：只保留最近一周修改的文件
    """
    import time
    
    try:
        stat_info = Path(file_path).stat()
        current_time = time.time()
        # 修改时间在一周内（7天 * 24小时 * 3600秒）
        return (current_time - stat_info.st_mtime) < 7 * 24 * 3600
    except OSError:
        return False


if __name__ == "__main__":
    from rich import print as rprint
    
    # 示例1：使用大小过滤器
    print("\n[bold green]示例1: 查找大于 1KB 的 Python 文件[/bold green]")
    config1 = FndConfig(
        suffixes={"py"},
        filter_fn=custom_size_filter,
        recursive=True
    )
    
    files1 = find_files("~/fnd", config1)
    rprint(f"找到 {len(files1)} 个大于 1KB 的 Python 文件")
    rprint(files1[:3])  # 显示前3个结果
    
    # 示例2：结合多种过滤器
    print("\n[bold green]示例2: 查找非临时文件的 Python 文件[/bold green]")
    config2 = FndConfig(
        suffixes={"py"},
        filter_fn=custom_extension_filter,
        recursive=True
    )
    
    files2 = find_files("~/fnd", config2)
    rprint(f"找到 {len(files2)} 个非临时的 Python 文件")
    rprint(files2[:3])  # 显示前3个结果
    
    # 示例3：组合使用内置过滤器和自定义过滤器
    print("\n[bold green]示例3: 查找包含 'core' 的大于 1KB 的 Python 文件[/bold green]")
    config3 = FndConfig(
        suffixes={"py"},
        include={"core"},
        filter_fn=custom_size_filter,
        recursive=True
    )
    
    files3 = find_files("~/fnd", config3)
    rprint(f"找到 {len(files3)} 个符合条件的文件")
    rprint(files3[:3])  # 显示前3个结果