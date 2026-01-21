#!/usr/bin/env python
"""
测试运行脚本

提供便捷的测试运行方式，包括覆盖率报告等。
"""

import sys
import subprocess
from pathlib import Path


def run_tests(
    coverage: bool = False,
    verbose: bool = True,
    path: str = "tests/",
) -> int:
    """
    运行测试
    
    参数:
        coverage: 是否生成覆盖率报告
        verbose: 是否显示详细信息
        path: 测试路径
    
    返回:
        退出代码
    """
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=core",
            "--cov=infrastructure",
            "--cov-report=html",
            "--cov-report=term",
        ])
    
    cmd.append(path)
    
    return subprocess.call(cmd)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="安静模式，不显示详细信息"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="tests/",
        help="测试路径（默认: tests/）"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        coverage=args.coverage,
        verbose=not args.quiet,
        path=args.path,
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
