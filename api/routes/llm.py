"""
LLM路由模块

提供LLM服务相关的API接口。
"""

import logging
from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from api.models.request import ChatRequest, StreamChatRequest, Message
from api.models.response import ChatResponse, ErrorResponse, UsageInfo
from api.dependencies import get_llm_service, get_agent_engine
from core.llm.service import LLMService
from core.llm.models import RoutingStrategy, ModelCapability
from core.agent.engine import AgentEngine, AgentError
from typing import Dict, Any, List
from datetime import datetime
import json

router = APIRouter()

# 设置日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
try:
    LOG_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"警告: 无法创建日志目录 {LOG_DIR}: {e}")

# 创建专用日志记录器
llm_logger = logging.getLogger("llm_api")
llm_logger.setLevel(logging.DEBUG)

# 避免重复添加处理器
if not llm_logger.handlers:
    # 文件处理器
    try:
        log_file = LOG_DIR / "llm_api.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        llm_logger.addHandler(file_handler)
        llm_logger.addHandler(console_handler)
        
        # 配置Agent引擎和Qwen适配器的日志也输出到同一个文件
        # 注意：AgentEngine使用 core.agent.engine.AgentEngine 作为logger名称
        agent_engine_logger = logging.getLogger("core.agent.engine")
        agent_engine_logger.setLevel(logging.DEBUG)
        if not agent_engine_logger.handlers:  # 避免重复添加
            agent_engine_logger.addHandler(file_handler)
            agent_engine_logger.addHandler(console_handler)
        agent_engine_logger.propagate = False  # 避免重复输出
        
        # AgentEngine类的logger
        agent_engine_class_logger = logging.getLogger("core.agent.engine.AgentEngine")
        agent_engine_class_logger.setLevel(logging.DEBUG)
        if not agent_engine_class_logger.handlers:  # 避免重复添加
            agent_engine_class_logger.addHandler(file_handler)
            agent_engine_class_logger.addHandler(console_handler)
        agent_engine_class_logger.propagate = False
        
        # Qwen适配器的logger
        qwen_adapter_logger = logging.getLogger("core.llm.adapters.qwen_adapter")
        qwen_adapter_logger.setLevel(logging.DEBUG)
        if not qwen_adapter_logger.handlers:  # 避免重复添加
            qwen_adapter_logger.addHandler(file_handler)
            qwen_adapter_logger.addHandler(console_handler)
        qwen_adapter_logger.propagate = False
        
        # QwenAdapter类的logger
        qwen_adapter_class_logger = logging.getLogger("core.llm.adapters.qwen_adapter.QwenAdapter")
        qwen_adapter_class_logger.setLevel(logging.DEBUG)
        if not qwen_adapter_class_logger.handlers:  # 避免重复添加
            qwen_adapter_class_logger.addHandler(file_handler)
            qwen_adapter_class_logger.addHandler(console_handler)
        qwen_adapter_class_logger.propagate = False
        
        # 测试日志
        llm_logger.info(f"LLM API日志系统初始化完成，日志文件: {log_file.absolute()}")
    except Exception as e:
        print(f"警告: 无法初始化日志系统: {e}")
        # 至少添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        llm_logger.addHandler(console_handler)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    agent_engine: AgentEngine = Depends(get_agent_engine),
) -> ChatResponse:
    """
    聊天接口
    
    发送消息列表，获取LLM响应。
    如果启用Agent模式，将通过Agent引擎执行任务并支持工具调用。
    
    参数:
        request: 聊天请求，包含消息列表、模型等参数
        llm_service: LLM服务实例（依赖注入）
        agent_engine: Agent引擎实例（依赖注入）
    
    返回:
        聊天响应，包含响应内容、Token使用信息等
        当启用Agent模式时，metadata中包含工具调用信息（tool_calls, iterations）
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        llm_logger.info(f"收到聊天请求: use_agent={request.use_agent}, model={request.model}, messages_count={len(request.messages)}")
        
        # Agent模式：调用Agent引擎执行任务
        if request.use_agent:
            llm_logger.info("使用Agent模式处理请求")
            # 将聊天消息转换为Agent任务的prompt
            # 取最后一条用户消息作为任务描述
            last_user_message = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                raise ValueError("在Agent模式下，至少需要一条用户消息。")
            
            llm_logger.info(f"Agent任务: {last_user_message[:100]}..., conversation_id={request.conversation_id}")
            
            # 调用Agent引擎
            agent_result = await agent_engine.run_task(
                task=last_user_message,
                conversation_id=request.conversation_id,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            # 提取Agent结果并构建ChatResponse
            content = agent_result.get("content", "")
            tool_calls = agent_result.get("tool_calls", [])
            iterations = agent_result.get("iterations", 1)
            metadata = agent_result.get("metadata", {})
            usage_info = metadata.get("usage", {})
            
            llm_logger.info(f"Agent任务完成: content_length={len(content)}, tool_calls_count={len(tool_calls)}, iterations={iterations}")
            llm_logger.debug(f"Agent结果详情: tool_calls={tool_calls}, metadata={metadata}")
            
            # 在metadata中包含工具调用信息
            metadata["tool_calls"] = tool_calls
            metadata["iterations"] = iterations
            
            return ChatResponse(
                content=content,
                model=metadata.get("model", request.model or "unknown"),
                usage=UsageInfo(
                    prompt_tokens=usage_info.get("prompt_tokens", 0),
                    completion_tokens=usage_info.get("completion_tokens", 0),
                    total_tokens=usage_info.get("total_tokens", 0),
                ),
                metadata=metadata,
            )
        
        # 普通LLM模式：直接调用LLM服务
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = await llm_service.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        return ChatResponse(
            content=response.content,
            model=response.model,
            usage=UsageInfo(
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
            ),
            metadata=response.metadata,
        )
        
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent执行失败: {str(e)}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM调用失败: {str(e)}",
        ) from e


@router.post("/chat/stream")
async def stream_chat(
    request: StreamChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    agent_engine: AgentEngine = Depends(get_agent_engine),
):
    """
    流式聊天接口
    
    发送消息列表，以流式方式返回LLM响应。
    如果启用Agent模式，将先执行Agent任务，然后流式返回最终结果。
    注意：Agent模式下的流式输出会先完成工具调用，然后流式返回最终结果。
    
    参数:
        request: 流式聊天请求
        llm_service: LLM服务实例（依赖注入）
        agent_engine: Agent引擎实例（依赖注入）
    
    返回:
        Server-Sent Events (SSE) 格式的流式响应
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # Agent模式：先执行Agent任务，然后流式返回结果
        if request.use_agent:
            # 将聊天消息转换为Agent任务的prompt
            last_user_message = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                raise ValueError("在Agent模式下，至少需要一条用户消息。")
            
            async def generate_agent_response():
                """生成Agent模式的流式响应"""
                try:
                    # 先执行Agent任务（这会执行工具调用等）
                    agent_result = await agent_engine.run_task(
                        task=last_user_message,
                        conversation_id=request.conversation_id,
                        model=request.model,
                        temperature=request.temperature,
                    )
                    
                    # 提取结果
                    content = agent_result.get("content", "")
                    tool_calls = agent_result.get("tool_calls", [])
                    iterations = agent_result.get("iterations", 1)
                    metadata = agent_result.get("metadata", {})
                    usage_info = metadata.get("usage", {})
                    
                    # 在metadata中包含工具调用信息
                    metadata["tool_calls"] = tool_calls
                    metadata["iterations"] = iterations
                    
                    # 流式返回最终结果（逐字符或逐词）
                    # 为了更好的体验，我们按词分割返回
                    words = content.split()
                    for i, word in enumerate(words):
                        chunk_content = word + (" " if i < len(words) - 1 else "")
                        data = {
                            "content": chunk_content,
                            "model": metadata.get("model", request.model or "unknown"),
                            "usage": usage_info if i == len(words) - 1 else {},  # 只在最后发送usage
                            "metadata": metadata if i == len(words) - 1 else {},  # 只在最后发送完整metadata
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    
                    # 发送结束标记
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_data = {
                        "error": str(e),
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            return StreamingResponse(
                generate_agent_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # 普通LLM模式：直接流式返回
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        async def generate_response():
            """生成流式响应"""
            try:
                async for chunk in llm_service.stream_chat(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature,
                ):
                    # 转换为SSE格式
                    data = {
                        "content": chunk.content,
                        "model": chunk.model,
                        "usage": chunk.usage,
                        "metadata": chunk.metadata,
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                # 发送错误信息
                error_data = {
                    "error": str(e),
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent执行失败: {str(e)}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"流式聊天失败: {str(e)}",
        ) from e


@router.get("/models", response_model=List[str])
async def list_models(
    llm_service: LLMService = Depends(get_llm_service),
) -> List[str]:
    """
    获取支持的模型列表
    
    返回:
        支持的模型名称列表
    
    参数:
        llm_service: LLM服务实例（依赖注入）
    """
    try:
        models = llm_service._registry.get_supported_models()
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型列表失败: {str(e)}",
        ) from e
