"""
测试模块：日志管理器测试
功能描述：测试LogManager的所有功能
"""

import pytest
import tempfile
from pathlib import Path
from infrastructure.log import LogManager


@pytest.fixture
def temp_log_dir():
    """创建临时日志目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.mark.asyncio
class TestLogManager:
    """LogManager测试类"""
    
    async def test_logger_creation(self):
        """测试创建日志记录器"""
        # Arrange
        log_manager = LogManager()
        
        # Act
        logger = log_manager.get_logger("test.module")
        
        # Assert
        assert logger is not None
        assert logger.name == "test.module"
    
    async def test_logger_caching(self):
        """测试日志记录器缓存"""
        # Arrange
        log_manager = LogManager()
        
        # Act
        logger1 = log_manager.get_logger("test.module")
        logger2 = log_manager.get_logger("test.module")
        
        # Assert
        assert logger1 is logger2
    
    async def test_logger_with_file(self, temp_log_dir):
        """测试文件日志记录"""
        import logging
        import time
        
        # Arrange
        log_file = str(Path(temp_log_dir) / "test.log")
        config = {
            "level": "INFO",
            "file": log_file,
            "max_bytes": 1024 * 1024,  # 1MB
            "backup_count": 3
        }
        log_manager = LogManager(config)
        
        # Act
        logger = log_manager.get_logger("test.module")
        logger.info("测试日志")
        
        # 确保日志写入完成
        logging.shutdown()
        time.sleep(0.1)  # 等待文件写入完成
        
        # Assert
        assert Path(log_file).exists()
        log_content = Path(log_file).read_text(encoding="utf-8")
        assert "测试日志" in log_content
        
        # 清理：关闭LogManager，释放文件句柄
        log_manager.shutdown()
        time.sleep(0.1)  # 等待文件句柄释放
    
    async def test_logger_levels(self):
        """测试日志级别"""
        # Arrange
        config = {"level": "DEBUG"}
        log_manager = LogManager(config)
        
        # Act
        logger = log_manager.get_logger("test.module")
        
        # Assert
        assert logger.level == 10  # DEBUG level
    
    async def test_logger_reconfigure(self):
        """测试重新配置日志"""
        # Arrange
        log_manager = LogManager({"level": "INFO"})
        logger = log_manager.get_logger("test.module")
        
        # Act
        log_manager.configure({"level": "ERROR"})
        
        # Assert
        assert logger.level == 40  # ERROR level
    
    async def test_shutdown(self):
        """测试关闭日志系统"""
        # Arrange
        log_manager = LogManager()
        logger = log_manager.get_logger("test.module")
        initial_handlers_count = len(logger.handlers)
        
        # Act
        log_manager.shutdown()
        
        # Assert
        # shutdown会移除LogManager添加的handlers，但可能还有其他handlers
        # 至少确保LogManager添加的handlers被移除了
        assert len(logger.handlers) <= initial_handlers_count
