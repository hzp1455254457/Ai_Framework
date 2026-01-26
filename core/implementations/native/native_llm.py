"""
模块名称：自研LLM提供者实现
功能描述：包装现有LLMService为ILLMProvider接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - NativeLLMProvider: 自研LLM提供者实现

依赖模块：
    - core.interfaces.llm: LLM提供者接口
    - core.llm.service: LLM服务
"""

from typing import List, Dict, Any, AsyncIterator, Optional
from core.interfaces.llm import ILLMProvider
from core.llm.service import LLMService
from core.llm.models import LLMResponse


class NativeLLMProvider(ILLMProvider):
    """
    自研LLM提供者实现
    
    包装现有LLMService为ILLMProvider接口，保持向后兼容。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化自研LLM提供者
        
        参数:
            config: 配置字典
        """
        self._config = config
        self._llm_service: Optional[LLMService] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化LLM服务"""
        if self._initialized:
            return
        
        self._llm_service = LLMService(self._config)
        await self._llm_service.initialize()
        self._initialized = True
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """
        发送聊天请求
        
        参数:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度参数
            max_tokens: 最大token数（可选）
            **kwargs: 其他参数
        
        返回:
            LLMResponse对象
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._llm_service:
            raise RuntimeError("LLM服务未初始化")
        
        return await self._llm_service.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        """
        流式聊天
        
        参数:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度参数
            **kwargs: 其他参数
        
        生成器:
            逐个返回LLMResponse对象
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._llm_service:
            raise RuntimeError("LLM服务未初始化")
        
        async for chunk in self._llm_service.stream_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs
        ):
            yield chunk
    
    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        返回:
            可用模型名称列表
        """
        if not self._llm_service:
            return []
        return self._llm_service.list_models()
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        返回:
            True表示健康可用，False表示不可用
        """
        if not self._initialized or not self._llm_service:
            return False
        
        try:
            result = await self._llm_service.health_check()
            return result.status.value == "healthy"
        except Exception:
            return False
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self._llm_service:
            await self._llm_service.cleanup()
        self._initialized = False
