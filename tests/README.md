# fnd 测试套件

这是一个针对 fnd 包的完整 pytest 测试套件，用于确保代码质量和功能正确性。

## 安装测试依赖

```bash
# 确保已安装项目和测试依赖
uv add --group dev pytest
```

## 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行所有测试并显示详细输出
python -m pytest -v

# 运行特定测试文件
python -m pytest tests/test_core.py

# 运行特定测试类
python -m pytest tests/test_core.py::TestFndConfig

# 运行特定测试方法
python -m pytest tests/test_core.py::TestFndConfig::test_default_config

# 运行测试并生成覆盖率报告（需要安装pytest-cov）
python -m pytest --cov=fnd
```

## 测试套件结构

测试套件包括以下主要部分：

### TestFndConfig
- 测试 FndConfig 数据类的各种配置选项

### TestIterFiles
- 测试 iter_files 函数的递归和非递归遍历功能
- 测试空目录处理

### TestListFiles  
- 测试 list_files 函数的列表包装功能

### TestMatchFilter
- 测试后缀过滤功能
- 测试包含关键词过滤功能（注意：关键词过滤要求文件名包含所有关键词）
- 测试自定义过滤器功能
- 测试组合过滤器功能

### TestFindFiles
- 测试主函数 find_files 的各种使用场景
- 测试后缀过滤、关键词过滤、递归搜索等功能
- 测试自定义过滤器功能
- 测试并行过滤功能

## 测试覆盖范围

- 核心功能的全面测试
- 边界情况处理
- 错误情况处理
- 性能相关的并行处理功能
- 各种参数组合的测试

## 配置

项目配置位于 [pyproject.toml](file:///home/clicko/fnd/pyproject.toml) 文件中，其中包含了 pytest 的配置。

## 扩展测试

要添加新功能的测试，请在相应的测试类中添加新的测试方法，或创建新的测试类。