#!/usr/bin/env bash

# 遇到错误、未定义变量或管道错误时立即退出
set -euo pipefail

# 颜色定义
export RC='\033[0m'
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[0;33m'
export BLUE='\033[0;34m'

# 定义需要测试的 Python 版本矩阵
PYTHON_VERSIONS=("3.10" "3.11" "3.12" "3.13" "3.14")

echo -e "${BLUE}===============================================${RC}"
echo -e "${BLUE}  开始模拟 GitHub Actions 本地 Matrix 测试流程  ${RC}"
echo -e "${BLUE}===============================================${RC}"
echo

# 检查本地是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}错误: 未检测到 uv，请先安装 uv后再运行此脚本。${RC}"
    exit 1
fi

FAILED_VERSIONS=()
PASSED_VERSIONS=()

# 循环执行测试
for version in "${PYTHON_VERSIONS[@]}"; do
    echo -e "${YELLOW}▶ 正在启动 Python ${version} 测试环境...${RC}"
    
    # 模拟 uv run --python <version> --frozen pytest tests/
    # uv 会自动下载本地缺失的 Python 版本
    if uv run --python "${version}" --frozen pytest tests/; then
        echo -e "${GREEN}✓ Python ${version} 测试通过！${RC}"
        PASSED_VERSIONS+=("${version}")
    else
        echo -e "${RED}✗ Python ${version} 测试失败！${RC}"
        FAILED_VERSIONS+=("${version}")
    fi
    echo -e "${BLUE}-----------------------------------------------${RC}"
done

# 打印最终结构化报告
echo
echo -e "${BLUE}=== 本地测试结果汇总 ===${RC}"
if [ ${#PASSED_VERSIONS[@]} -ne 0 ]; then
    echo -e "${GREEN}通过版本: ${PASSED_VERSIONS[*]}${RC}"
fi

if [ ${#FAILED_VERSIONS[@]} -ne 0 ]; then
    echo -e "${RED}失败版本: ${FAILED_VERSIONS[*]}${RC}"
    echo
    echo -e "${RED}⚠️ 存在未通过测试的版本，请修正后再提交代码。${RC}"
    exit 1
else
    echo
    echo -e "${GREEN}🎉 所有版本测试全绿，可以放心推送到 GitHub！${RC}"
    exit 0
fi