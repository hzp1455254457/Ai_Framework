"""
模块名称：配置验证器模块
功能描述：验证配置的有效性和完整性
创建日期：2026-01-21
最后更新：2026-01-21
维护者：AI框架团队

主要类：
    - ConfigValidator: 配置验证器
    - ConfigError: 配置错误异常
    - ConfigValidationError: 配置验证错误异常

依赖模块：
    - typing: 类型注解
"""

from typing import Dict, Any, List, Optional
from .migrator import ConfigMigrator


class ConfigError(Exception):
    """配置错误异常基类"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证错误异常"""
    pass


class ConfigValidator:
    """
    配置验证器
    
    验证配置的有效性和完整性。
    
    示例:
        >>> validator = ConfigValidator()
        >>> validator.validate(config)
    """
    
    def __init__(self, required_keys: Optional[List[str]] = None) -> None:
        """
        初始化配置验证器
        
        参数:
            required_keys: 必需配置键列表（可选）
        """
        self._required_keys: List[str] = required_keys or []
    
    def validate(self, config: Dict[str, Any], auto_migrate: bool = False) -> List[str]:
        """
        验证配置有效性
        
        检查：
        1. 配置是否为字典类型
        2. 必需键是否存在
        3. 配置值类型是否正确（可选）
        4. 加密配置格式是否正确（如果存在）
        5. 新架构配置项的兼容性
        
        参数:
            config: 配置字典
            auto_migrate: 是否自动迁移旧版本配置（默认False）
        
        返回:
            错误列表（空列表表示验证通过）
        """
        errors: List[str] = []
        
        if not isinstance(config, dict):
            errors.append("配置必须是字典类型")
            return errors
        
        # 如果启用自动迁移，先迁移配置
        if auto_migrate:
            migrator = ConfigMigrator()
            version = migrator.detect_version(config)
            if version != migrator._current_version:
                try:
                    config = migrator.migrate(config)
                except Exception as e:
                    errors.append(f"配置迁移失败: {e}")
                    return errors
        
        # 验证配置兼容性
        migrator = ConfigMigrator()
        compatibility_issues = migrator.validate_compatibility(config)
        if compatibility_issues:
            errors.extend(compatibility_issues)
        
        # 检查必需键
        for key in self._required_keys:
            if key not in config:
                errors.append(f"缺少必需配置项: {key}")
        
        # 验证加密配置格式（递归检查）
        try:
            self._validate_encryption_format(config)
        except ConfigValidationError as e:
            errors.append(str(e))
        
        # 验证LLM配置
        if "llm" in config:
            errors.extend(self._validate_llm_config(config["llm"]))
        
        return errors
    
    def _validate_llm_config(self, llm_config: Dict[str, Any]) -> List[str]:
        """验证LLM配置"""
        errors: List[str] = []
        
        # 验证必需字段
        if "default_model" not in llm_config:
            errors.append("llm.default_model 是必需的")
        
        # 验证超时时间
        if "timeout" in llm_config:
            timeout = llm_config["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("llm.timeout 必须是正数")
        
        # 验证重试次数
        if "max_retries" in llm_config:
            max_retries = llm_config["max_retries"]
            if not isinstance(max_retries, int) or max_retries < 0:
                errors.append("llm.max_retries 必须是非负整数")
        
        # 验证路由配置
        if "enable_routing" in llm_config and llm_config["enable_routing"]:
            if "default_routing_strategy" in llm_config:
                strategy = llm_config["default_routing_strategy"]
                valid_strategies = ["cost_first", "performance_first", "availability_first", "balanced", "manual"]
                if strategy not in valid_strategies:
                    errors.append(f"llm.default_routing_strategy 必须是以下之一: {', '.join(valid_strategies)}")
        
        # 验证性能优化配置
        if "performance" in llm_config:
            perf_config = llm_config["performance"]
            if perf_config.get("enable_connection_pool", False):
                if "max_connections" in perf_config:
                    max_conn = perf_config["max_connections"]
                    if not isinstance(max_conn, int) or max_conn <= 0:
                        errors.append("llm.performance.max_connections 必须是正整数")
                if "cache_ttl" in perf_config:
                    cache_ttl = perf_config["cache_ttl"]
                    if not isinstance(cache_ttl, (int, float)) or cache_ttl <= 0:
                        errors.append("llm.performance.cache_ttl 必须是正数")
        
        # 验证成本管理配置
        if "cost" in llm_config:
            cost_config = llm_config["cost"]
            if cost_config.get("budget_enabled", False):
                daily_budget = cost_config.get("daily_budget", 0.0)
                monthly_budget = cost_config.get("monthly_budget", 0.0)
                if not isinstance(daily_budget, (int, float)) or daily_budget < 0:
                    errors.append("llm.cost.daily_budget 必须是非负数")
                if not isinstance(monthly_budget, (int, float)) or monthly_budget < 0:
                    errors.append("llm.cost.monthly_budget 必须是非负数")
                if daily_budget == 0.0 and monthly_budget == 0.0:
                    errors.append("启用预算管理时，至少需要设置 daily_budget 或 monthly_budget")
                alert_threshold = cost_config.get("alert_threshold", 0.8)
                if not isinstance(alert_threshold, (int, float)) or alert_threshold < 0 or alert_threshold > 1:
                    errors.append("llm.cost.alert_threshold 必须是0-1之间的数")
        
        # 验证监控配置
        if "monitoring" in llm_config:
            monitoring_config = llm_config["monitoring"]
            if monitoring_config.get("tracing_enabled", False):
                if "tracing" in monitoring_config:
                    tracing_config = monitoring_config["tracing"]
                    if "max_traces" in tracing_config:
                        max_traces = tracing_config["max_traces"]
                        if not isinstance(max_traces, int) or max_traces <= 0:
                            errors.append("llm.monitoring.tracing.max_traces 必须是正整数")
                    if "trace_ttl" in tracing_config:
                        trace_ttl = tracing_config["trace_ttl"]
                        if not isinstance(trace_ttl, (int, float)) or trace_ttl <= 0:
                            errors.append("llm.monitoring.tracing.trace_ttl 必须是正数")
        
        return errors
    
    def _validate_encryption_format(self, config: Dict[str, Any], path: str = "") -> None:
        """
        验证加密配置格式
        
        递归检查配置中的加密值格式是否正确。
        
        参数:
            config: 配置字典
            path: 当前配置路径（用于错误提示）
        
        异常:
            ConfigValidationError: 加密格式错误时抛出
        """
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                # 递归检查嵌套字典
                self._validate_encryption_format(value, current_path)
            elif isinstance(value, str) and value.startswith("encrypted:"):
                # 验证加密格式
                encrypted_value = value[10:]  # 移除 "encrypted:" 前缀
                parts = encrypted_value.split(":")
                if len(parts) != 4:
                    raise ConfigValidationError(
                        f"配置项 {current_path} 的加密格式错误，应为 'salt:iv:ciphertext:tag'"
                    )
    
    def add_required_key(self, key: str) -> None:
        """
        添加必需配置键
        
        参数:
            key: 配置键
        """
        if key not in self._required_keys:
            self._required_keys.append(key)
    
    def remove_required_key(self, key: str) -> None:
        """
        移除必需配置键
        
        参数:
            key: 配置键
        """
        if key in self._required_keys:
            self._required_keys.remove(key)
