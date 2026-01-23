"""
模块名称：配置迁移工具模块
功能描述：提供配置迁移和验证能力，支持配置版本升级和兼容性检查
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - ConfigMigrator: 配置迁移器

依赖模块：
    - typing: 类型注解
    - pathlib: 路径处理
    - yaml: YAML文件处理
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import shutil
from datetime import datetime


class ConfigMigrator:
    """
    配置迁移器
    
    提供配置版本升级和兼容性检查能力。
    
    特性：
        - 配置版本检测
        - 自动迁移旧版本配置
        - 配置兼容性检查
        - 备份原配置文件
    
    示例:
        >>> migrator = ConfigMigrator()
        >>> migrated_config = migrator.migrate(config_dict)
        >>> migrator.backup_config("config/default.yaml")
    """
    
    def __init__(self, config_dir: Optional[str] = None) -> None:
        """
        初始化配置迁移器
        
        参数:
            config_dir: 配置目录路径（可选）
        """
        self._config_dir = Path(config_dir) if config_dir else Path("config")
        self._current_version = "2.0"  # 当前配置版本
    
    def detect_version(self, config: Dict[str, Any]) -> str:
        """
        检测配置版本
        
        参数:
            config: 配置字典
        
        返回:
            配置版本字符串
        """
        # 检查是否有版本字段
        if "config_version" in config:
            return str(config["config_version"])
        
        # 根据配置结构推断版本
        # v1.0: 没有路由、性能优化、成本管理等新功能
        # v2.0: 包含路由、性能优化、成本管理、监控等新功能
        
        has_routing = "llm" in config and "enable_routing" in config.get("llm", {})
        has_performance = "llm" in config and "performance" in config.get("llm", {})
        has_cost = "llm" in config and "cost" in config.get("llm", {})
        has_monitoring = "llm" in config and "monitoring" in config.get("llm", {})
        
        if has_routing or has_performance or has_cost or has_monitoring:
            return "2.0"
        
        return "1.0"
    
    def migrate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        迁移配置到最新版本
        
        参数:
            config: 配置字典
        
        返回:
            迁移后的配置字典
        """
        version = self.detect_version(config)
        
        if version == self._current_version:
            # 已经是最新版本，只需添加版本号
            if "config_version" not in config:
                config["config_version"] = self._current_version
            return config
        
        # 从v1.0迁移到v2.0
        if version == "1.0":
            config = self._migrate_v1_to_v2(config)
        
        # 添加版本号
        config["config_version"] = self._current_version
        
        return config
    
    def _migrate_v1_to_v2(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从v1.0迁移到v2.0（内部方法）
        
        参数:
            config: v1.0配置字典
        
        返回:
            v2.0配置字典
        """
        migrated = config.copy()
        
        # 确保llm配置存在
        if "llm" not in migrated:
            migrated["llm"] = {}
        
        llm_config = migrated["llm"]
        
        # 添加路由配置（默认禁用，保持向后兼容）
        if "enable_routing" not in llm_config:
            llm_config["enable_routing"] = False
        if "default_routing_strategy" not in llm_config:
            llm_config["default_routing_strategy"] = "balanced"
        
        # 添加性能优化配置（默认启用，提高性能）
        if "performance" not in llm_config:
            llm_config["performance"] = {
                "enable_connection_pool": True,
                "max_connections": 100,
                "max_keepalive_connections": 20,
                "connection_timeout": 30.0,
                "enable_cache": True,
                "cache_ttl": 3600.0,
                "cache_max_size": 1000,
                "enable_deduplication": True,
                "batch_size": 10,
                "max_concurrent": 5,
            }
        
        # 添加成本管理配置（默认启用）
        if "cost" not in llm_config:
            llm_config["cost"] = {
                "enabled": True,
                "daily_budget": 0.0,
                "monthly_budget": 0.0,
                "alert_threshold": 0.8,
                "budget_enabled": False,
            }
        
        # 添加监控配置（默认启用）
        if "monitoring" not in llm_config:
            llm_config["monitoring"] = {
                "enabled": True,
                "tracing_enabled": True,
                "tracing": {
                    "max_traces": 1000,
                    "trace_ttl": 3600,
                },
            }
        
        return migrated
    
    def backup_config(self, config_file: str) -> str:
        """
        备份配置文件
        
        参数:
            config_file: 配置文件路径
        
        返回:
            备份文件路径
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # 生成备份文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.parent / f"{config_path.stem}_backup_{timestamp}{config_path.suffix}"
        
        # 复制文件
        shutil.copy2(config_path, backup_path)
        
        return str(backup_path)
    
    def migrate_config_file(self, config_file: str, backup: bool = True) -> Dict[str, Any]:
        """
        迁移配置文件
        
        参数:
            config_file: 配置文件路径
            backup: 是否备份原文件（默认True）
        
        返回:
            迁移后的配置字典
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # 备份原文件
        if backup:
            backup_path = self.backup_config(config_file)
            print(f"已备份配置文件到: {backup_path}")
        
        # 读取配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        
        # 检测版本
        version = self.detect_version(config)
        print(f"检测到配置版本: {version}")
        
        # 迁移配置
        if version != self._current_version:
            print(f"开始迁移配置从 {version} 到 {self._current_version}")
            config = self.migrate(config)
            
            # 保存迁移后的配置
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            print(f"配置迁移完成，已保存到: {config_file}")
        else:
            print("配置已是最新版本，无需迁移")
        
        return config
    
    def validate_compatibility(self, config: Dict[str, Any]) -> List[str]:
        """
        验证配置兼容性
        
        参数:
            config: 配置字典
        
        返回:
            兼容性问题列表（空列表表示无问题）
        """
        issues = []
        
        # 检查必需配置项
        if "llm" not in config:
            issues.append("缺少 'llm' 配置节")
            return issues
        
        llm_config = config["llm"]
        
        # 检查适配器配置
        if "adapters" not in llm_config:
            issues.append("缺少 'llm.adapters' 配置节")
        
        # 检查新架构配置项（如果启用了路由）
        if llm_config.get("enable_routing", False):
            if "default_routing_strategy" not in llm_config:
                issues.append("启用路由时，缺少 'llm.default_routing_strategy' 配置")
        
        # 检查性能优化配置
        if "performance" in llm_config:
            perf_config = llm_config["performance"]
            if perf_config.get("enable_connection_pool", False):
                if "max_connections" not in perf_config:
                    issues.append("启用连接池时，缺少 'llm.performance.max_connections' 配置")
        
        # 检查成本管理配置
        if "cost" in llm_config:
            cost_config = llm_config["cost"]
            if cost_config.get("budget_enabled", False):
                if cost_config.get("daily_budget", 0.0) == 0.0 and cost_config.get("monthly_budget", 0.0) == 0.0:
                    issues.append("启用预算管理时，至少需要设置 daily_budget 或 monthly_budget")
        
        # 检查监控配置
        if "monitoring" in llm_config:
            monitoring_config = llm_config["monitoring"]
            if monitoring_config.get("tracing_enabled", False):
                if "tracing" not in monitoring_config:
                    issues.append("启用追踪时，缺少 'llm.monitoring.tracing' 配置")
        
        return issues
