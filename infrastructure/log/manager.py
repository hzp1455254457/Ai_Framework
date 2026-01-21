"""
模块名称：日志管理器模块
功能描述：提供统一的日志管理能力，支持结构化日志、多级别日志、日志轮转
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - LogManager: 日志管理器主类

依赖模块：
    - logging: Python标准库日志模块
    - typing: 类型注解
"""

import sys
from typing import Dict, Any, Optional
from logging import Logger, getLogger, StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LogManager:
    """
    日志管理器
    
    提供统一的日志管理能力，支持：
    - 结构化日志
    - 多级别日志
    - 日志轮转
    - 日志归档
    
    特性：
        - 统一的日志格式
        - 支持文件和控制台输出
        - 支持日志轮转
        - 可配置日志级别
    
    示例:
        >>> log_manager = LogManager(config)
        >>> logger = log_manager.get_logger("my_module")
        >>> logger.info("这是一条日志")
    
    属性:
        _config: 日志配置
        _loggers: 日志记录器缓存
        _handlers: 日志处理器列表
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化日志管理器
        
        参数:
            config: 日志配置字典（可选）
                包含：
                - level: 日志级别（默认INFO）
                - format: 日志格式（可选）
                - file: 日志文件路径（可选）
                - max_bytes: 日志文件最大大小（默认10MB）
                - backup_count: 备份文件数量（默认5）
        """
        self._config: Dict[str, Any] = config or {}
        self._loggers: Dict[str, Logger] = {}
        self._handlers: list = []
        
        # 配置日志系统
        self.configure(self._config)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        配置日志系统
        
        参数:
            config: 日志配置字典
        """
        self._config.update(config)
        
        # 获取配置
        level = self._config.get("level", "INFO")
        log_format = self._config.get(
            "format",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_file = self._config.get("file")
        max_bytes = self._config.get("max_bytes", 10 * 1024 * 1024)  # 10MB
        backup_count = self._config.get("backup_count", 5)
        
        # 创建格式化器
        from logging import Formatter
        formatter = Formatter(log_format)
        
        # 清除现有处理器
        for handler in self._handlers:
            handler.close()
        self._handlers.clear()
        
        # 添加控制台处理器
        console_handler = StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        self._handlers.append(console_handler)
        
        # 添加文件处理器（如果配置了日志文件）
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            self._handlers.append(file_handler)
        
        # 更新所有现有日志记录器
        for logger in self._loggers.values():
            logger.handlers.clear()
            logger.setLevel(level)
            for handler in self._handlers:
                logger.addHandler(handler)
    
    def get_logger(self, name: str) -> Logger:
        """
        获取日志记录器
        
        如果日志记录器已存在，返回缓存的实例；否则创建新的实例。
        
        参数:
            name: 日志记录器名称（通常是模块名）
        
        返回:
            Logger实例
        
        示例:
            >>> logger = log_manager.get_logger("core.llm")
            >>> logger.info("LLM服务启动")
        """
        if name not in self._loggers:
            logger = getLogger(name)
            
            # 设置日志级别
            level = self._config.get("level", "INFO")
            logger.setLevel(level)
            
            # 添加处理器
            for handler in self._handlers:
                logger.addHandler(handler)
            
            # 防止日志传播到根日志记录器
            logger.propagate = False
            
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def shutdown(self) -> None:
        """
        关闭日志系统
        
        确保所有日志已写入并关闭所有处理器。
        """
        # 刷新所有日志记录器
        for logger in self._loggers.values():
            for handler in logger.handlers:
                handler.flush()
                handler.close()
        
        # 关闭所有处理器
        for handler in self._handlers:
            handler.flush()
            handler.close()
        
        self._handlers.clear()
        self._loggers.clear()
