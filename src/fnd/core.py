
import os
from pathlib import Path
from typing import Callable, Iterable, Iterator, TypeAlias
from dataclasses import dataclass


from rich.progress import track

# 类型定义
AnyPath: TypeAlias = str | Path
FilterFunc = Callable[[AnyPath], bool]


@dataclass
class FndConfig:
    """文件查找配置"""
    suffixes: Iterable[str] | None = None  # 如 ["py", "txt"]
    include: Iterable[str] | None = None
    recursive: bool = True
    filter_fn: FilterFunc | None = None
    verbose: bool = True


def iter_files(
    root: AnyPath, 
    recursive: bool = True
) -> Iterator[str]:
    """
    列出目录下的所有文件（迭代器版本）
    
    Args:
        root: 要搜索的目录
        recursive: 是否递归搜索子目录. 默认为 True.
    
    Yields:
        str: 文件路径，逐个产出
    """
    root = str(root)

    if not recursive:
        with os.scandir(root) as it:
            for entry in it:
                if entry.is_file():
                    yield entry.path
        return

    stack = [root]

    while stack:
        current = stack.pop()

        try:
            with os.scandir(current) as it:
                for entry in it:
                    if entry.is_file(follow_symlinks=True):
                        yield entry.path
                    elif entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)

        except PermissionError:
            pass


def list_files(root: AnyPath, recursive: bool = True) -> list[str]:
    """ 
    列出目录下的所有文件 
    
    Args:
        root (str | Path): 要搜索的目录
        recursive (bool, optional): 是否递归搜索子目录. 默认为 True.
    
    Returns:
        list[str]: 包含所有文件路径的列表
    """
    return list(iter_files(root, recursive=recursive))


def _match_filter(
    path: str,
    suffixes_set: set[str] | None = None,
    include_keywords: list[str] | None = None,
    filter_fn: FilterFunc | None = None
) -> bool:
    """
    根据过滤条件判断路径是否应该被包含
    
    Args:
        path: 要检查的文件路径
        suffixes_set: 允许的文件扩展名集合（小写）
        include_keywords: 文件名中必须包含的关键字列表
        filter_fn: 自定义过滤函数
    
    Returns:
        bool: 如果路径应该被包含则返回 True，否则返回 False
    """
    name = path.rsplit("/", 1)[-1]

    if suffixes_set is not None:
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        if ext not in suffixes_set:
            return False

    if include_keywords is not None:
        if not all(k in name for k in include_keywords):
            return False

    if filter_fn is not None and not filter_fn(path):
        return False

    return True


def find_files(
    root: AnyPath,
    config: FndConfig | None = None
) -> list[str]:
    """
    查找符合指定条件的文件
    
    Args:
        root: 搜索的根目录
        config: 文件查找配置
    
    Returns:
        list[str]: 符合条件的文件路径列表
    """
    if config is None:
        config = FndConfig()
    
    root_path = str(root)

    suffixes_set = {s.lower() for s in config.suffixes} if config.suffixes else None
    include_keywords = list(config.include) if config.include else None

    paths = list_files(root_path) if config.recursive else list_files(root_path, recursive=False)
    # paths = iter_files(root_path) if config.recursive else iter_files(root_path, recursive=False)

    result: list[str] = []

    track_iter = (
        track(paths, description="查找文件...")
        if config.verbose
        else paths
    )

    for path in track_iter:
        if _match_filter(path, suffixes_set, include_keywords, config.filter_fn):
            result.append(path)

    return result


if __name__ == "__main__":

    from codetiming import Timer
    from rich import print as rprint

    root = "/usr"
    
    # suffixes = {".so"}
    include = {"conf"}

    print("开始测试串行搜索")
    with Timer("find_files", text="串行搜索用时 {:0.4f}"):
        config = FndConfig(
            # suffixes=suffixes,
            include=include,
            recursive=True,
        )
        files = find_files(
            root=root, 
            config=config,
        )
    files = sorted(files)

    rprint(files[:3])
    rprint(len(files))