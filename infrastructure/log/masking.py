"""
模块名称：数据脱敏服务模块
功能描述：提供敏感数据检测和脱敏功能，用于日志和错误信息
创建日期：2026-01-22
最后更新：2026-01-22
维护者：AI框架团队

主要类：
    - DataMaskingService: 数据脱敏服务主类

依赖模块：
    - re: 正则表达式
    - hashlib: 哈希算法
    - typing: 类型注解
"""

import re
import hashlib
from typing import Dict, Any, Optional, List, Pattern, Callable
from enum import Enum


class MaskingMode(str, Enum):
    """脱敏模式枚举"""
    PARTIAL = "partial"  # 部分隐藏：保留前后部分
    FULL = "full"  # 完全隐藏：全部替换为占位符
    HASH = "hash"  # 哈希脱敏：使用哈希值（用于调试）


class DataMaskingService:
    """
    数据脱敏服务
    
    提供敏感数据检测和脱敏功能，支持：
    - 多种脱敏模式（部分隐藏、完全隐藏、哈希）
    - 预定义敏感数据模式（API密钥、邮箱、手机号等）
    - 自定义脱敏规则
    - 性能优化（正则表达式预编译）
    
    特性：
        - 自动检测常见敏感数据格式
        - 支持自定义脱敏规则
        - 可配置脱敏模式
        - 高性能（使用预编译正则表达式）
    
    示例：
        >>> service = DataMaskingService()
        >>> masked = service.mask_text("API key: sk-1234567890abcdef")
        >>> print(masked)  # "API key: sk-****...****ef"
    
    属性:
        _patterns: 预编译的正则表达式模式字典
        _mode: 脱敏模式
        _custom_rules: 自定义脱敏规则列表
        _enabled: 是否启用脱敏
    """
    
    # 预定义的敏感数据模式
    DEFAULT_PATTERNS: Dict[str, str] = {
        # API密钥模式
        "api_key_sk": r"sk-[a-zA-Z0-9]{16,}",  # OpenAI/DALL-E API密钥（至少16个字符）
        "api_key_sk_live": r"sk_live_[a-zA-Z0-9]{20,}",  # Stripe API密钥
        "api_key_sk_test": r"sk_test_[a-zA-Z0-9]{20,}",  # Stripe测试密钥
        "api_key_pk": r"pk-[a-zA-Z0-9]{16,}",  # 公钥
        "api_key_env": r"[A-Z_]+_API_KEY\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{16,}['\"]?",  # 环境变量格式
        
        # 邮箱模式
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        
        # 手机号模式（中国）
        "phone_cn": r"1[3-9]\d{9}",
        
        # 身份证号模式（中国）
        "id_card_cn": r"\d{17}[\dXx]",
        
        # 银行卡号模式
        "bank_card": r"\d{16,19}",
        
        # 密码模式（常见格式）
        "password": r"password\s*[:=]\s*['\"]?[^'\"]+['\"]?",
        "pwd": r"pwd\s*[:=]\s*['\"]?[^'\"]+['\"]?",
    }
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化数据脱敏服务
        
        参数:
            config: 配置字典（可选）
                包含：
                - enabled: 是否启用脱敏（默认True）
                - mode: 脱敏模式（partial/full/hash，默认partial）
                - patterns: 自定义脱敏规则（可选）
                - keep_prefix: 部分隐藏时保留的前缀长度（默认3）
                - keep_suffix: 部分隐藏时保留的后缀长度（默认2）
        """
        self._config: Dict[str, Any] = config or {}
        self._enabled: bool = self._config.get("enabled", True)
        self._mode: MaskingMode = MaskingMode(
            self._config.get("mode", "partial")
        )
        self._keep_prefix: int = self._config.get("keep_prefix", 3)
        self._keep_suffix: int = self._config.get("keep_suffix", 2)
        
        # 预编译正则表达式模式
        self._patterns: Dict[str, Pattern] = {}
        self._compile_patterns()
        
        # 自定义规则
        self._custom_rules: List[Dict[str, Any]] = self._config.get("custom_rules", [])
        self._compile_custom_rules()
    
    def _compile_patterns(self) -> None:
        """编译预定义的正则表达式模式"""
        for name, pattern in self.DEFAULT_PATTERNS.items():
            try:
                self._patterns[name] = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                # 如果模式编译失败，记录警告但继续
                import logging
                logging.warning(f"脱敏模式编译失败 {name}: {e}")
    
    def _compile_custom_rules(self) -> None:
        """编译自定义脱敏规则"""
        for rule in self._custom_rules:
            pattern_str = rule.get("pattern")
            if pattern_str:
                try:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    rule["compiled_pattern"] = pattern
                except re.error as e:
                    import logging
                    logging.warning(f"自定义脱敏规则编译失败: {e}")
    
    def mask_text(self, text: str) -> str:
        """
        脱敏文本中的敏感数据
        
        参数:
            text: 原始文本
        
        返回:
            脱敏后的文本
        
        示例:
            >>> service = DataMaskingService()
            >>> masked = service.mask_text("API key: sk-1234567890abcdef")
            >>> print(masked)  # "API key: sk-****...****ef"
        """
        if not self._enabled or not text:
            return text
        
        result = text
        
        # 应用预定义模式
        for name, pattern in self._patterns.items():
            result = pattern.sub(
                lambda m: self._mask_match(m.group(0)),
                result
            )
        
        # 应用自定义规则
        for rule in self._custom_rules:
            compiled_pattern = rule.get("compiled_pattern")
            if compiled_pattern:
                result = compiled_pattern.sub(
                    lambda m: self._mask_match(m.group(0)),
                    result
                )
        
        return result
    
    def _mask_match(self, match: str) -> str:
        """
        对匹配到的敏感数据进行脱敏
        
        参数:
            match: 匹配到的敏感数据字符串
        
        返回:
            脱敏后的字符串
        """
        if self._mode == MaskingMode.PARTIAL:
            return self._mask_partial(match)
        elif self._mode == MaskingMode.FULL:
            return self._mask_full(match)
        elif self._mode == MaskingMode.HASH:
            return self._mask_hash(match)
        else:
            return match
    
    def _mask_partial(self, text: str) -> str:
        """
        部分隐藏脱敏
        
        保留前后部分，中间用星号替换。
        
        参数:
            text: 原始文本
        
        返回:
            脱敏后的文本
        
        示例:
            >>> service._mask_partial("sk-1234567890abcdef")
            "sk-****...****ef"
        """
        if len(text) <= self._keep_prefix + self._keep_suffix:
            # 如果文本太短，完全隐藏
            return "***MASKED***"
        
        prefix = text[:self._keep_prefix]
        suffix = text[-self._keep_suffix:] if self._keep_suffix > 0 else ""
        middle = "*" * min(8, len(text) - self._keep_prefix - self._keep_suffix)
        
        if suffix:
            return f"{prefix}{middle}...{suffix}"
        else:
            return f"{prefix}{middle}"
    
    def _mask_full(self, text: str) -> str:
        """
        完全隐藏脱敏
        
        全部替换为占位符。
        
        参数:
            text: 原始文本
        
        返回:
            脱敏后的文本
        
        示例:
            >>> service._mask_full("sk-1234567890abcdef")
            "***MASKED***"
        """
        return "***MASKED***"
    
    def _mask_hash(self, text: str) -> str:
        """
        哈希脱敏
        
        使用SHA256哈希值（用于调试）。
        
        参数:
            text: 原始文本
        
        返回:
            脱敏后的文本（格式：sha256:前8位哈希值）
        
        示例:
            >>> service._mask_hash("sk-1234567890abcdef")
            "sha256:a1b2c3d4"
        """
        hash_value = hashlib.sha256(text.encode()).hexdigest()
        return f"sha256:{hash_value[:8]}"
    
    def mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        脱敏字典中的敏感数据
        
        递归处理字典中的所有值，对字符串值进行脱敏。
        
        参数:
            data: 原始字典
        
        返回:
            脱敏后的字典
        
        示例:
            >>> service.mask_dict({"api_key": "sk-1234567890", "name": "test"})
            {"api_key": "sk-****...****90", "name": "test"}
        """
        if not self._enabled:
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.mask_text(value)
            elif isinstance(value, dict):
                result[key] = self.mask_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.mask_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def add_custom_rule(
        self,
        name: str,
        pattern: str,
        mode: Optional[MaskingMode] = None,
    ) -> None:
        """
        添加自定义脱敏规则
        
        参数:
            name: 规则名称
            pattern: 正则表达式模式
            mode: 脱敏模式（可选，使用默认模式）
        
        示例:
            >>> service.add_custom_rule("custom_id", r"ID:\d+")
        """
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            rule = {
                "name": name,
                "pattern": pattern,
                "compiled_pattern": compiled_pattern,
                "mode": mode or self._mode,
            }
            self._custom_rules.append(rule)
        except re.error as e:
            raise ValueError(f"无效的正则表达式模式: {e}") from e
    
    def enable(self) -> None:
        """启用脱敏功能"""
        self._enabled = True
    
    def disable(self) -> None:
        """禁用脱敏功能"""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """检查是否启用脱敏功能"""
        return self._enabled


def mask_sensitive_data(
    text: str,
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    工具函数：脱敏文本中的敏感数据
    
    参数:
        text: 原始文本
        config: 配置字典（可选）
    
    返回:
        脱敏后的文本
    
    示例:
        >>> masked = mask_sensitive_data("API key: sk-1234567890abcdef")
        >>> print(masked)  # "API key: sk-****...****ef"
    """
    service = DataMaskingService(config)
    return service.mask_text(text)
