"""
pytest配置和fixture定义

提供测试中使用的公共fixture和配置。

说明：
    - 此文件会被pytest自动发现和加载
    - 所有fixture可以被所有测试文件使用
    - 配置项会影响所有测试的运行方式
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """示例配置fixture"""
    return {
        "api_key": "test-api-key",
        "timeout": 30,
        "max_retries": 3,
        "base_url": "https://api.example.com",
    }


@pytest.fixture
def empty_config() -> Dict[str, Any]:
    """空配置fixture（用于测试错误场景）"""
    return {}


@pytest.fixture
def llm_service_config() -> Dict[str, Any]:
    """LLM服务配置fixture"""
    return {
        "llm": {
            "default_model": "gpt-3.5-turbo",
            "timeout": 30,
            "max_retries": 3,
            "auto_discover_adapters": False,  # 测试时禁用自动发现
        }
    }


@pytest.fixture
def adapter_config() -> Dict[str, Any]:
    """适配器配置fixture"""
    return {
        "api_key": "test-api-key",
        "base_url": "https://api.test.com",
    }
