from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from multiprocessing import cpu_count
from pathlib import Path
import os
from rich import print as rprint
from rich.progress import track

# 3.10+ 兼容的类型定义
AnyPath = str | Path
FilterFunc = Callable[[str], bool]


@dataclass
class FndConfig:
    """文件查找配置"""

    suffixes: Iterable[str] | None = None  # 支持包含点的后缀集合，如 [".py", ".txt"]
    include: Iterable[str] | None = None
    recursive: bool = True
    filter_fn: FilterFunc | None = None
    verbose: bool = True


def iter_files(root: AnyPath, recursive: bool = True) -> Iterator[str]:
    """纯字符串高性能遍历"""
    root_str = str(root)

    if not recursive:
        try:
            with os.scandir(root_str) as it:
                for entry in it:
                    if entry.is_file():
                        yield entry.path
        except PermissionError:
            pass
        return

    stack = [root_str]
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
    """列出目录下的所有文件（列表包装）"""
    return list(iter_files(root, recursive=recursive))


def _match_filter(
    path: str,
    suffixes_set: set[str] | None = None,
    include_keywords: list[str] | None = None,
    filter_fn: FilterFunc | None = None,
) -> bool:
    """极致压榨性能的过滤函数，基于 os.path 且免除 lstrip"""

    # 后缀过滤：C 实现的 splitext 返回形式如 ('/path/to/file', '.py')
    if suffixes_set is not None:
        ext = os.path.splitext(path)[1].lower()  # 直接拿到带点的后缀转小写
        if ext not in suffixes_set:
            return False

    # 关键字过滤
    if include_keywords is not None:
        name = os.path.basename(path)
        if not all(k in name for k in include_keywords):
            return False

    # 自定义过滤函数
    if filter_fn is not None and not filter_fn(path):
        return False

    return True


def find_files(
    root: AnyPath,
    config: FndConfig | None = None,
    filter_threads: int = 1, 
) -> list[str]:
    """
    查找符合指定条件的文件, 推荐仅在明确筛选耗时较长的情况使用并行筛选

    Args:
        root: 搜索的根目录
        config: 文件查找配置
        parallel: 是否并行筛选，适用于筛选耗时较长的情况
        filter_threads: 并行筛选时的线程数, 默认不开多线程, 传入 -1 则使用 cpu_count - 1 个线程

    Returns:
        list[str]: 符合条件的文件路径列表
    """
    cfg = config or FndConfig()

    # 外层一次性强力清洗：确保 suffixes_set 内部全部带有 "." 且为小写
    suffixes_set = (
        {s.lower() if s.startswith(".") else f".{s.lower()}" for s in cfg.suffixes}
        if cfg.suffixes
        else None
    )
    include_keywords = list(cfg.include) if cfg.include else None

    # 获取基础路径文件（纯字符串列表）
    paths = list_files(root, recursive=cfg.recursive)

    track_iter = (
        track(paths, description="fnd 查找文件...") if cfg.verbose else paths
    )

    # 过滤单步闭包
    def check_path(p: str) -> str | None:
        if _match_filter(p, suffixes_set, include_keywords, cfg.filter_fn):
            return p
        return None

    # 串行筛选分支：海象运算符配合列表推导式
    if filter_threads == 1:
        return [res for p in track_iter if (res := check_path(p)) is not None]

    # 并行筛选分支
    max_workers = cpu_count() - 1 if filter_threads == -1 else max(1, filter_threads)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_path, track_iter))

    return [r for r in results if r is not None]


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