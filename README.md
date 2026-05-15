# fnd - 可能是 Python 中的最快的文件搜索库

`fnd` 是一个快速的文件查找工具，提供了一个灵活的 Python API 来搜索文件系统中的文件。

## 特性

- 支持按文件后缀名搜索
- 支持按关键词过滤文件路径
- 提供并行搜索功能以提高性能
- 支持自定义过滤函数
- 与流行的命令行工具 `fd` 和 `find` 具有相似的功能

## 性能对比示例

项目提供了 `examples/fd_vs_find_vs_fnd.py` 示例脚本来比较不同工具的性能：

- `fd`: 一个现代、快速的文件搜索工具（Rust 编写）
- `find`: 传统的 Unix 文件搜索命令
- `fnd`: 本项目的 Python 实现

### 运行示例

```bash
python examples/fd_vs_find_vs_fnd.py
```

此脚本会比较这三种工具在指定目录（默认为 `/usr`）中搜索特定类型文件（如 `.so` 动态库文件）的性能，并输出每种工具的执行时间。

## 自定义过滤器示例

项目还提供了 `examples/custom_filter_example.py` 示例来展示如何使用自定义过滤器：

```bash
python examples/custom_filter_example.py
```

该示例展示了以下几种自定义过滤器的使用：

- 按文件大小过滤（例如：只保留大于 1KB 的文件）
- 按文件类型过滤（例如：排除临时文件和隐藏文件）
- 按修改时间过滤（例如：只保留最近一周修改的文件）

### 示例输出格式

```
fd 搜索用时 0.1234
fd 搜索到 X 个文件
['/path/to/file1.so', '/path/to/file2.so', ...]

find 搜索用时 0.5678
find 搜索到 X 个文件
['/path/to/file1.so', '/path/to/file2.so', ...]

fnd 搜索用时 0.9012
fnd 搜索到 X 个文件
['/path/to/file1.so', '/path/to/file2.so', ...]

fnd 搜索并行筛选用时 0.4567
fnd 并行搜索到 X 个文件
['/path/to/file1.so', '/path/to/file2.so', ...]
```

## 安装

```bash
pip install fnd
```

## 使用方法

```python
from fnd import find_files
from fnd.core import FndConfig

# 创建配置
config = FndConfig(
    suffixes={"py", "txt"},  # 按后缀名搜索
    include={"src", "test"},  # 文件路径中包含特定关键词
    recursive=True,  # 递归搜索子目录
    filter_fn=lambda path: True  # 自定义过滤函数
)

# 搜索文件
files = find_files("/path/to/search", config)

# 使用并行处理提高性能
files_parallel = find_files("/path/to/search", config, filter_threads=-1)
```

## 配置选项

- `suffixes`: 设置要搜索的文件扩展名集合
- `include`: 设置文件路径中必须包含的关键词集合
- `recursive`: 是否递归搜索子目录
- `filter_fn`: 自定义过滤函数，接收文件路径作为参数，返回布尔值
- `verbose`: 是否显示详细信息

## 自定义过滤器

您可以使用 `filter_fn` 参数传递一个自定义过滤函数，该函数接收文件路径作为字符串参数并返回布尔值。当函数返回 `True` 时，文件会被包含在结果中；否则会被过滤掉。

常见用途包括：

- 按文件大小过滤
- 按修改时间过滤
- 按权限过滤
- 按其他文件属性过滤

## 并行处理

通过设置 `filter_threads` 参数，可以在文件过滤阶段启用并行处理以提高性能。
注意：推荐仅在明确筛选耗时较长的情况使用并行筛选，否则可能会引入额外的开销。
## 许可证

本项目基于 MIT License 开源.