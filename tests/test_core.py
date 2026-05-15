"""fnd 包核心功能的 pytest 测试套件"""

import os
from pathlib import Path
from typing import Generator
import tempfile
import shutil

import pytest
from fnd.core import (
    FndConfig,
    find_files,
    iter_files,
    list_files,
    _match_filter
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """创建临时目录用于测试"""
    temp_path = Path(tempfile.mkdtemp())
    try:
        # 创建一些测试文件和子目录
        # 根目录文件
        (temp_path / "test.txt").write_text("test content")
        (temp_path / "test.py").write_text("# Python file")
        (temp_path / "test.js").write_text("// JavaScript file")
        
        # 子目录
        sub_dir = temp_path / "subdir"
        sub_dir.mkdir()
        (sub_dir / "nested.txt").write_text("nested content")
        (sub_dir / "nested.py").write_text("# Nested Python file")
        (sub_dir / ".hidden").write_text("hidden file")
        
        # 更深层级的目录
        deep_dir = sub_dir / "deep"
        deep_dir.mkdir()
        (deep_dir / "deep.txt").write_text("deep content")
        (deep_dir / "deep.py").write_text("# Deep Python file")
        
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


class TestFndConfig:
    """测试 FndConfig 数据类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = FndConfig()
        assert config.suffixes is None
        assert config.include is None
        assert config.recursive is True
        assert config.filter_fn is None
        assert config.verbose is True
    
    def test_custom_config(self):
        """测试自定义配置"""
        def dummy_filter(path: str) -> bool:
            return True
        
        config = FndConfig(
            suffixes=["py", "js"],
            include=["test", "main"],
            recursive=False,
            filter_fn=dummy_filter,
            verbose=False
        )
        assert config.suffixes == ["py", "js"]
        assert config.include == ["test", "main"]
        assert config.recursive is False
        assert config.filter_fn is dummy_filter
        assert config.verbose is False


class TestIterFiles:
    """测试 iter_files 函数"""
    
    def test_iter_files_recursive(self, temp_dir: Path):
        """测试递归遍历"""
        files = list(iter_files(temp_dir, recursive=True))
        assert len(files) >= 6  # 至少应包含我们创建的文件
        assert any("test.py" in f for f in files)
        assert any("nested.py" in f for f in files)
        assert any("deep.py" in f for f in files)
    
    def test_iter_files_non_recursive(self, temp_dir: Path):
        """测试非递归遍历"""
        files = list(iter_files(temp_dir, recursive=False))
        assert len(files) == 3  # 只有根目录的3个文件
        assert all("subdir" not in f for f in files)  # 不应包含子目录中的文件
    
    def test_iter_files_empty_dir(self):
        """测试空目录"""
        with tempfile.TemporaryDirectory() as tmp:
            files = list(iter_files(tmp, recursive=True))
            assert len(files) == 0


class TestListFiles:
    """测试 list_files 函数"""
    
    def test_list_files_recursive(self, temp_dir: Path):
        """测试递归列出文件"""
        files = list_files(temp_dir, recursive=True)
        assert isinstance(files, list)
        assert len(files) >= 6  # 至少应包含我们创建的文件
        assert any("test.py" in f for f in files)
    
    def test_list_files_non_recursive(self, temp_dir: Path):
        """测试非递归列出文件"""
        files = list_files(temp_dir, recursive=False)
        assert isinstance(files, list)
        assert len(files) == 3  # 只有根目录的文件


class TestMatchFilter:
    """测试 _match_filter 函数"""
    
    def test_suffix_filter(self):
        """测试后缀过滤"""
        suffixes_set = {".py", ".js"}
        
        # 匹配的文件
        assert _match_filter("/path/test.py", suffixes_set=suffixes_set)
        assert _match_filter("/path/test.js", suffixes_set=suffixes_set)
        
        # 不匹配的文件
        assert not _match_filter("/path/test.txt", suffixes_set=suffixes_set)
        assert not _match_filter("/path/test", suffixes_set=suffixes_set)
    
    def test_case_insensitive_suffix(self):
        """测试后缀过滤大小写不敏感"""
        suffixes_set = {".py", ".js"}  # 实际上后缀比较是小写的
        assert _match_filter("/path/test.py", suffixes_set=suffixes_set)
        assert _match_filter("/path/test.PY", suffixes_set=suffixes_set)
        assert _match_filter("/path/test.JS", suffixes_set=suffixes_set)
    
    def test_include_filter(self):
        """测试包含关键词过滤"""
        # 注意：include_keywords 要求文件名包含所有关键词
        include_keywords_test = ["test"]
        include_keywords_main = ["main"]
        include_keywords_both = ["test", "main"]  # 文件名需同时包含test和main
        
        # 包含关键词的文件 - 需要正确传递参数，按照函数签名顺序
        # _match_filter(path, suffixes_set=None, include_keywords=None, filter_fn=None)
        assert _match_filter("/path/test.py", None, include_keywords_test)  # test.py 包含 "test"
        assert _match_filter("/path/main.js", None, include_keywords_main)  # main.js 包含 "main"
        assert _match_filter("/path/test_main.txt", None, include_keywords_both)  # test_main.txt 包含 "test" 和 "main"
        
        # 不包含关键词的文件
        assert not _match_filter("/path/other.txt", None, include_keywords_test)  # other.txt 不包含 "test"
        assert not _match_filter("/path/test.py", None, include_keywords_both)  # test.py 不包含 "main"
        assert not _match_filter("/path/main.js", None, include_keywords_both)  # main.js 不包含 "test"
    
    def test_combined_filters(self):
        """测试组合过滤器"""
        suffixes_set = {".py"}
        include_keywords = ["test"]
        
        # 同时满足两个条件
        assert _match_filter("/path/test.py", suffixes_set, include_keywords)
        
        # 只满足其中一个条件
        assert not _match_filter("/path/main.py", suffixes_set, include_keywords)  # 不包含test
        assert not _match_filter("/path/test.txt", suffixes_set, include_keywords)  # 不是.py
    
    def test_custom_filter(self):
        """测试自定义过滤器"""
        def custom_filter(path: str) -> bool:
            return "special" in path.lower()
        
        # 满足自定义过滤器
        assert _match_filter("/path/special.txt", None, None, custom_filter)
        
        # 不满足自定义过滤器
        assert not _match_filter("/path/normal.txt", None, None, custom_filter)
    
    def test_all_filters_combined(self):
        """测试所有过滤器组合"""
        suffixes_set = {".py"}
        include_keywords = ["test"]
        def custom_filter(path: str) -> bool:
            return "special" not in path.lower()
        
        # 满足所有条件
        assert _match_filter("/path/test.py", suffixes_set, include_keywords, custom_filter)
        
        # 不满足任一条件
        assert not _match_filter("/path/main.py", suffixes_set, include_keywords, custom_filter)  # 缺少test
        assert not _match_filter("/path/test.txt", suffixes_set, include_keywords, custom_filter)  # 缺少.py
        assert not _match_filter("/path/test_special.py", suffixes_set, include_keywords, custom_filter)  # 满足special，但custom_filter返回False


class TestFindFiles:
    """测试 find_files 函数"""
    
    def test_find_all_files(self, temp_dir: Path):
        """测试查找所有文件"""
        files = find_files(temp_dir, FndConfig(recursive=True, verbose=False))
        assert len(files) >= 6  # 至少包含我们创建的文件
        
        # 检查是否包含了各级目录的文件
        assert any("test.py" in f for f in files)
        assert any("nested.py" in f for f in files)
        assert any("deep.py" in f for f in files)
    
    def test_find_by_suffix(self, temp_dir: Path):
        """测试按后缀查找"""
        config = FndConfig(suffixes=["py"], recursive=True, verbose=False)
        files = find_files(temp_dir, config)
        
        # 所有结果都应该是.py文件
        for f in files:
            assert Path(f).suffix == ".py"
        
        # 应该包含各级目录的.py文件
        assert any("test.py" in f for f in files)
        assert any("nested.py" in f for f in files)
        assert any("deep.py" in f for f in files)
    
    def test_find_by_include(self, temp_dir: Path):
        """测试按包含关键词查找"""
        config = FndConfig(include=["nested"], recursive=True, verbose=False)
        files = find_files(temp_dir, config)
        
        # 所有结果都应该包含"nested"
        for f in files:
            assert "nested" in Path(f).name.lower()
    
    def test_find_by_suffix_and_include(self, temp_dir: Path):
        """测试同时使用后缀和包含关键词过滤"""
        config = FndConfig(suffixes=["py"], include=["nested"], recursive=True, verbose=False)
        files = find_files(temp_dir, config)
        
        # 所有结果都应是.py文件且包含"nested"
        for f in files:
            assert Path(f).suffix == ".py"
            assert "nested" in Path(f).name.lower()
    
    def test_find_non_recursive(self, temp_dir: Path):
        """测试非递归查找"""
        config = FndConfig(recursive=False, verbose=False)
        files = find_files(temp_dir, config)
        
        # 只应返回根目录的文件
        assert len(files) == 3  # 我们在根目录创建了3个文件
        assert all(str(temp_dir) in f for f in files)
        assert all("subdir" not in f for f in files)
    
    def test_find_with_custom_filter(self, temp_dir: Path):
        """测试使用自定义过滤器"""
        def size_filter(path: str) -> bool:
            try:
                return Path(path).stat().st_size > 5  # 文件大小大于5字节
            except:
                return False
        
        config = FndConfig(filter_fn=size_filter, recursive=True, verbose=False)
        files = find_files(temp_dir, config)
        
        # 所有返回的文件都应大于5字节
        for f in files:
            assert Path(f).stat().st_size > 5
    
    def test_suffix_normalization(self, temp_dir: Path):
        """测试后缀规范化（自动添加点）"""
        # 测试不带点的后缀
        config = FndConfig(suffixes=["py"], recursive=True, verbose=False)
        files1 = find_files(temp_dir, config)
        
        # 测试带点的后缀
        config = FndConfig(suffixes=[".py"], recursive=True, verbose=False)
        files2 = find_files(temp_dir, config)
        
        # 结果应该相同
        assert len(files1) == len(files2)
    
    def test_parallel_filtering(self, temp_dir: Path):
        """测试并行过滤功能"""
        config = FndConfig(suffixes=["py"], recursive=True, verbose=False)
        
        # 串行过滤
        files_seq = find_files(temp_dir, config, filter_threads=1)
        
        # 并行过滤（使用2个线程）
        files_par = find_files(temp_dir, config, filter_threads=2)
        
        # 结果应该相同，只是性能可能不同
        assert len(files_seq) == len(files_par)
        assert set(files_seq) == set(files_par)
    
    def test_negative_thread_count(self, temp_dir: Path):
        """测试负数线程数（使用CPU核心数-1）"""
        config = FndConfig(suffixes=["py"], recursive=True, verbose=False)
        
        # 使用CPU核心数-1的线程
        files = find_files(temp_dir, config, filter_threads=-1)
        
        # 应该返回正确的结果
        assert isinstance(files, list)
        for f in files:
            assert Path(f).suffix == ".py"


def test_example_usage():
    """测试与示例代码类似的用法"""
    def custom_size_filter(file_path: str) -> bool:
        """自定义过滤器：只保留大于 10 字节的文件"""
        try:
            return Path(file_path).stat().st_size > 10
        except OSError:
            return False
    
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        
        # 创建测试文件
        (tmp_path / "small.txt").write_text("small")  # 5字节
        (tmp_path / "large.txt").write_text("this is a larger file content")  # >10字节
        (tmp_path / "large.py").write_text("# This is a larger Python file with content")  # >10字节
        
        # 测试自定义过滤器
        config = FndConfig(
            suffixes=["txt"],
            filter_fn=custom_size_filter,
            recursive=True,
            verbose=False
        )
        
        files = find_files(tmp_path, config)
        
        # 应该只返回大于10字节的txt文件
        assert len(files) == 1
        assert "large.txt" in str(files[0])