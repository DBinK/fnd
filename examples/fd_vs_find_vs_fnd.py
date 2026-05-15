import subprocess
from pathlib import Path

from codetiming import Timer
from rich import print as rprint

from fnd.core import FndConfig, find_files


def find_files_fd(root: str | Path, config=None):
    root = str(root)
    
    if config is None:
        from fnd.core import FndConfig
        config = FndConfig()

    cmd = ["fd"]

    for s in config.suffixes or []:
        cmd += ["-e", s.lstrip(".")]

    for k in config.include or ["."]:
        cmd.append(k)

    cmd.append(root)

    rprint(f"[bold cyan]Executing:[/bold cyan] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return []

    paths = result.stdout.strip().splitlines() 

    # return [Path(p) for p in paths if p] 
    return paths


def find_files_find(
    root: str | Path, 
    config=None
) -> list[str]:
    root_path = Path(root)
    if not root_path.exists():
        return []
    
    if config is None:
        from fnd.core import FndConfig
        config = FndConfig()

    # 基础命令
    cmd: list[str] = ["find", str(root_path), "-type", "f"]

    # 1. 处理后缀 (Suffixes) -> 使用 -name
    if config.suffixes:
        cmd.append("(")
        for i, s in enumerate(config.suffixes):
            if i > 0:
                cmd.append("-o")
            pattern = f"*{s}" if s.startswith(".") else f"*.{s}"
            cmd.extend(["-name", pattern])
        cmd.append(")")

    # 2. 处理包含关键词 (Include) -> 使用 -path 模拟
    # find 的 -path 匹配的是全路径，所以需要前后加 *
    if config.include:
        cmd.append("(")
        for i, k in enumerate(config.include):
            if i > 0:
                cmd.append("-o")
            cmd.extend(["-path", f"*{k}*"])
        cmd.append(")")

    # 调试打印：在 subprocess 中 list 形式不需要加反斜杠
    # 但为了让你在终端能直接跑，我用 rich 格式化一下
    rprint(f"[bold blue]Executing:[/bold blue] {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    # if result.returncode != 0:
    #     rprint(f"[bold red]Error:[/bold red] {result.stderr}")
    #     return []

    paths = [p for p in result.stdout.splitlines() if p]
    
    return paths



if __name__ == "__main__":


    root = "/usr"
    # root = "/var"
    
    suffixes = {"so"}
    include = {"lib"}

    # 组装配置对象
    config = FndConfig(
        suffixes=suffixes,
        include=include,
        recursive=True,
    )
    
    # 开始所有搜索测试

    with Timer(text="fd 搜索用时 {:0.4f}"):
        files = find_files_fd(root, config)
        # files = [Path(file) for file in files]

    # files = sorted(files)
    rprint(f"fd 搜索到 {len(files)} 个文件")
    rprint(files[:3])
    print("")


    with Timer(text="find 搜索用时 {:0.4f}"):
        files = find_files_find(root, config)
        # files = [Path(file) for file in files]
    
    # files = sorted(files)
    rprint(f"find 搜索到 {len(files)} 个文件")
    rprint(files[:3])
    print("")


    with Timer(text="fnd 搜索用时 {:0.4f}"):
        files = find_files(root, config)
        # files = [Path(file) for file in files]
        
    # files = sorted(files)
    rprint(f"fnd 搜索到 {len(files)} 个文件")
    rprint(files[:3])
    print("")


    with Timer(text="fnd 搜索并行筛选用时 {:0.4f}"):
        files = find_files(root, config, filter_threads=-1)
        # files = [Path(file) for file in files]
        
    # files = sorted(files)
    rprint(f"fnd 并行搜索到 {len(files)} 个文件")
    rprint(files[:3])
    print("")