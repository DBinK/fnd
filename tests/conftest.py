"""pytest 配置文件"""

import sys
from pathlib import Path

# 添加项目源码路径到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))