"""
LLM路由模块

提供LLM服务相关的API接口。
"""

from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from api.models.request import ChatRequest, StreamChatRequest, Message
from api.models.response import ChatResponse, ErrorResponse, UsageInfo
from api.dependencies import get_llm_service
from core.llm.service import LLMService
import json

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
) -> ChatResponse:
    """
    聊天接口
    
    发送消息列表，获取LLM响应。
    
    参数:
        request: 聊天请求，包含消息列表、模型等参数
        llm_service: LLM服务实例（依赖注入）
    
    返回:
        聊天响应，包含响应内容、Token使用信息等
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # 调用LLM服务
        response = await llm_service.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        # 构建响应
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
):
    """
    流式聊天接口
    
    发送消息列表，以流式方式返回LLM响应。
    
    参数:
        request: 流式聊天请求
        llm_service: LLM服务实例（依赖注入）
    
    返回:
        Server-Sent Events (SSE) 格式的流式响应
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # 转换消息格式
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
