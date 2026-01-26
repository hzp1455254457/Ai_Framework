"""
模块名称：LangChain LLM提供者实现
功能描述：将现有LLMService包装为LangChain LLM，实现ILLMProvider接口
创建日期：2026-01-26
最后更新：2026-01-26
维护者：AI框架团队

主要类：
    - LangChainLLMWrapper: LangChain LLM包装器（将ILLMProvider包装为BaseLLM）
    - LangChainLLMProvider: LangChain LLM提供者实现

依赖模块：
    - core.interfaces.llm: LLM提供者接口
    - core.llm.service: LLM服务
    - langchain: LangChain框架（可选）
"""

from typing import List, Dict, Any, AsyncIterator, Optional, Iterator
import asyncio

try:
    # 新版本LangChain使用langchain_core
    from langchain_core.language_models.llms import BaseLLM
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult, Generation
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # 尝试旧版本导入路径（向后兼容）
    try:
        from langchain.llms.base import BaseLLM
        from langchain.callbacks.base import BaseCallbackHandler
        from langchain.schema import LLMResult, Generation
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        BaseLLM = None
        BaseCallbackHandler = None
        LLMResult = None
        Generation = None

from core.interfaces.llm import ILLMProvider
from core.llm.service import LLMService
from core.llm.models import LLMResponse


class LangChainLLMWrapper(BaseLLM if LANGCHAIN_AVAILABLE else object):
    """
    LangChain LLM包装器
    
    将ILLMProvider包装为LangChain BaseLLM，使其可以在LangChain生态中使用。
    
    特性：
        - 实现LangChain BaseLLM接口
        - 支持同步和异步调用
        - 支持流式输出
        - 参数映射（temperature、max_tokens等）
    """
    
    def __init__(self, llm_provider: ILLMProvider):
        """
        初始化LangChain LLM包装器
        
        参数:
            llm_provider: LLM提供者实例
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装，请运行: pip install langchain")
        
        super().__init__()
        self._llm_provider = llm_provider
        self._model_name: Optional[str] = None
    
    @property
    def _llm_type(self) -> str:
        """返回LLM类型标识"""
        return "illm_provider_wrapper"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回用于标识此LLM的参数"""
        return {
            "llm_provider_type": type(self._llm_provider).__name__,
            "model_name": self._model_name,
        }
    
    async def agenerate_prompt(
        self,
        prompts: List[Any],
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResult:
        """
        异步生成（从PromptValue）
        
        覆盖基类方法，直接调用_agenerate以避免callbacks参数冲突。
        
        参数:
            prompts: PromptValue列表
            stop: 停止词列表（可选）
            **kwargs: 其他参数（可能包含callbacks）
        
        返回:
            LLMResult对象
        """
        # 调试日志：检查调用参数
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"agenerate_prompt called with stop={stop}, kwargs keys={list(kwargs.keys())}")
        if 'callbacks' in kwargs:
            logger.debug(f"  -> callbacks found in kwargs: {kwargs['callbacks']}")
        
        # 从kwargs中移除callbacks，避免重复传递
        # 这是关键修复：确保callbacks不会在多处传递
        callbacks = kwargs.pop("callbacks", None)
        kwargs.pop("callback_manager", None)
        
        # 将PromptValue转换为字符串
        prompt_strings = [p.to_string() if hasattr(p, 'to_string') else str(p) for p in prompts]
        
        # 直接调用_agenerate，绕过agenerate中可能重复传递callbacks的逻辑
        return await self._agenerate(
            prompt_strings,
            stop=stop,
            run_manager=None,
            **kwargs
        )
    
    async def agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        callbacks: Optional[Any] = None,
        **kwargs: Any
    ) -> LLMResult:
        """
        异步生成（覆盖基类方法）
        
        覆盖基类方法，确保callbacks不会重复传递。
        
        参数:
            prompts: 提示字符串列表
            stop: 停止词列表（可选）
            callbacks: 回调（可选）
            **kwargs: 其他参数
        
        返回:
            LLMResult对象
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"agenerate called with stop={stop}, kwargs keys={list(kwargs.keys())}")
        if 'callbacks' in kwargs:
            logger.debug(f"  -> callbacks found in kwargs: {kwargs['callbacks']}")
        
        # 从kwargs中移除callbacks，避免传递给agenerate_prompt时重复
        kwargs.pop("callbacks", None)
        kwargs.pop("callback_manager", None)
        
        # 将PromptValue转换为字符串并调用agenerate_prompt
        # 注意：这里传递callbacks作为显式参数，而不是在kwargs中
        return await self.agenerate_prompt(
            prompts,
            stop=stop,
            callbacks=callbacks,
            **kwargs
        )
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> LLMResult:
        """
        生成方法（LangChain接口，新版本要求）
        
        参数:
            prompts: 提示列表
            stop: 停止词列表（可选）
            run_manager: 回调管理器（可选）
            **kwargs: 其他参数（注意：可能包含callbacks，需要过滤）
        
        返回:
            LLMResult对象
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装")
        
        # 从kwargs中移除callbacks和run_manager，避免重复传递
        filtered_kwargs = {
            k: v for k, v in kwargs.items() 
            if k not in ["callbacks", "run_manager", "callback_manager"]
        }
        
        generations = []
        
        for prompt in prompts:
            # 将prompt转换为消息列表
            messages = [{"role": "user", "content": prompt}]
            
            # 提取参数
            temperature = filtered_kwargs.get("temperature", 0.7)
            max_tokens = filtered_kwargs.get("max_tokens")
            model = filtered_kwargs.get("model") or self._model_name
            
            # 同步调用（使用asyncio）
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，创建新任务
                    try:
                        import nest_asyncio
                        nest_asyncio.apply()
                    except ImportError:
                        pass
                response = loop.run_until_complete(
                    self._llm_provider.chat(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **{k: v for k, v in filtered_kwargs.items() if k not in ["temperature", "max_tokens", "model"]}
                    )
                )
            except RuntimeError:
                # 如果没有事件循环，创建新的
                response = asyncio.run(
                    self._llm_provider.chat(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **{k: v for k, v in filtered_kwargs.items() if k not in ["temperature", "max_tokens", "model"]}
                    )
                )
            
            # 转换为LangChain格式
            generation = Generation(text=response.content)
            generations.append([generation])
        
        return LLMResult(generations=generations)
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> str:
        """
        同步调用LLM（LangChain接口，兼容旧版本）
        
        参数:
            prompt: 输入提示
            stop: 停止词列表（可选）
            run_manager: 回调管理器（可选）
            **kwargs: 其他参数
        
        返回:
            LLM响应文本
        """
        # 使用_generate方法
        result = self._generate([prompt], stop=stop, run_manager=run_manager, **kwargs)
        if result.generations and len(result.generations) > 0:
            if result.generations[0] and len(result.generations[0]) > 0:
                return result.generations[0][0].text
        return ""
    
    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> LLMResult:
        """
        异步生成（LangChain接口）
        
        参数:
            prompts: 提示列表
            stop: 停止词列表（可选）
            run_manager: 回调管理器（可选）
            **kwargs: 其他参数（注意：可能包含callbacks，需要过滤）
        
        返回:
            LLMResult对象
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装")
        
        # 从kwargs中移除callbacks和run_manager，避免重复传递
        # callbacks可能通过agenerate_prompt传递，run_manager通过_agenerate传递
        filtered_kwargs = {
            k: v for k, v in kwargs.items() 
            if k not in ["callbacks", "run_manager", "callback_manager"]
        }
        
        generations = []
        
        for prompt in prompts:
            # 将prompt转换为消息列表
            messages = [{"role": "user", "content": prompt}]
            
            # 提取参数
            temperature = filtered_kwargs.get("temperature", 0.7)
            max_tokens = filtered_kwargs.get("max_tokens")
            model = filtered_kwargs.get("model") or self._model_name
            
            # 调用ILLMProvider（不传递callbacks相关参数）
            response = await self._llm_provider.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **{k: v for k, v in filtered_kwargs.items() if k not in ["temperature", "max_tokens", "model"]}
            )
            
            # 转换为LangChain格式
            generation = Generation(text=response.content)
            generations.append([generation])
        
        return LLMResult(generations=generations)
    
    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> Iterator[str]:
        """
        流式输出（同步接口）
        
        参数:
            prompt: 输入提示
            stop: 停止词列表（可选）
            run_manager: 回调管理器（可选）
            **kwargs: 其他参数
        
        生成器:
            逐个返回响应文本块
        """
        # 将prompt转换为消息列表
        messages = [{"role": "user", "content": prompt}]
        
        # 提取参数
        temperature = kwargs.get("temperature", 0.7)
        model = kwargs.get("model") or self._model_name
        
        # 同步流式调用（简化实现）
        # 注意：LangChain的_stream方法在某些版本中可能不支持，这里提供基础实现
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用asyncio.create_task
                import nest_asyncio
                nest_asyncio.apply()
            
            async def _collect_chunks():
                chunks = []
                async for chunk in self._llm_provider.stream_chat(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    **{k: v for k, v in kwargs.items() if k not in ["temperature", "model"]}
                ):
                    chunks.append(chunk.content)
                return chunks
            
            chunks = loop.run_until_complete(_collect_chunks())
            for chunk in chunks:
                yield chunk
        except RuntimeError:
            # 如果没有事件循环，创建新的
            async def _collect_chunks():
                chunks = []
                async for chunk in self._llm_provider.stream_chat(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    **{k: v for k, v in kwargs.items() if k not in ["temperature", "model"]}
                ):
                    chunks.append(chunk.content)
                return chunks
            
            chunks = asyncio.run(_collect_chunks())
            for chunk in chunks:
                yield chunk


class LangChainLLMProvider(ILLMProvider):
    """
    LangChain LLM提供者实现
    
    将现有LLMService包装为LangChain LLM，实现ILLMProvider接口。
    支持LangChain生态的工具和组件。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LangChain LLM提供者
        
        参数:
            config: 配置字典
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain未安装，请运行: pip install langchain")
        
        self._config = config
        self._llm_service: Optional[LLMService] = None
        self._langchain_llm: Optional[Any] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化LLM服务"""
        if self._initialized:
            return
        
        # 创建LLMService实例
        self._llm_service = LLMService(self._config)
        await self._llm_service.initialize()
        
        # 创建LangChain LLM包装器
        # 注意：这里我们使用LangChainLLMProvider本身作为ILLMProvider
        # 因为LangChainLLMProvider已经实现了ILLMProvider接口
        self._langchain_llm = LangChainLLMWrapper(self)
        
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
        
        # 使用LLMService处理请求
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
