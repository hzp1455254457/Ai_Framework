#!/usr/bin/env python3
"""测试日志系统"""

import logging
from pathlib import Path
import sys

# 设置日志目录
LOG_DIR = Path(__file__).parent / "logs"
try:
    LOG_DIR.mkdir(exist_ok=True)
    print(f"✅ 日志目录: {LOG_DIR.absolute()}")
except Exception as e:
    print(f"❌ 无法创建日志目录: {e}")
    sys.exit(1)

# 测试agent_api日志
print("\n=== 测试 agent_api 日志 ===")
agent_logger = logging.getLogger("agent_api")
agent_logger.setLevel(logging.DEBUG)

# 清除现有处理器
agent_logger.handlers.clear()

try:
    log_file = LOG_DIR / "agent_api.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    agent_logger.addHandler(file_handler)
    agent_logger.addHandler(console_handler)
    
    agent_logger.info("测试日志消息 - agent_api")
    agent_logger.debug("调试日志消息")
    
    print(f"✅ 日志已写入: {log_file.absolute()}")
    if log_file.exists():
        print(f"   文件大小: {log_file.stat().st_size} 字节")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"   总行数: {len(lines)}")
            if lines:
                print(f"   最后一行: {lines[-1].strip()}")
except Exception as e:
    print(f"❌ 日志测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试llm_api日志
print("\n=== 测试 llm_api 日志 ===")
llm_logger = logging.getLogger("llm_api")
llm_logger.setLevel(logging.DEBUG)

# 清除现有处理器
llm_logger.handlers.clear()

try:
    log_file = LOG_DIR / "llm_api.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    llm_logger.addHandler(file_handler)
    llm_logger.addHandler(console_handler)
    
    llm_logger.info("测试日志消息 - llm_api")
    llm_logger.debug("调试日志消息")
    
    print(f"✅ 日志已写入: {log_file.absolute()}")
    if log_file.exists():
        print(f"   文件大小: {log_file.stat().st_size} 字节")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"   总行数: {len(lines)}")
            if lines:
                print(f"   最后一行: {lines[-1].strip()}")
except Exception as e:
    print(f"❌ 日志测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")
