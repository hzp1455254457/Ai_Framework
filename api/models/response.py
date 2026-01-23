"""
API响应模型模块

定义所有API响应的数据模型。
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class UsageInfo(BaseModel):
    """Token使用信息"""
    
    prompt_tokens: int = Field(0, description="提示Token数量")
    completion_tokens: int = Field(0, description="完成Token数量")
    total_tokens: int = Field(0, description="总Token数量")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    
    content: str = Field(..., description="响应内容")
    model: str = Field(..., description="使用的模型名称")
    usage: UsageInfo = Field(..., description="Token使用信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "你好！我是AI助手。",
                "model": "gpt-3.5-turbo",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                },
                "metadata": {}
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="错误详情")
    code: Optional[int] = Field(None, description="错误代码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "LLM调用失败",
                "detail": "API密钥无效",
                "code": 401
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    
    status: str = Field(..., description="服务状态：healthy/unhealthy")
    version: str = Field(..., description="服务版本")
    adapters: list = Field(default_factory=list, description="可用适配器列表")
    models: list = Field(default_factory=list, description="支持的模型列表")


class AdapterHealthStatus(BaseModel):
    """适配器健康状态模型"""
    
    name: str = Field(..., description="适配器名称")
    status: str = Field(..., description="健康状态：healthy/unhealthy/unknown")
    message: Optional[str] = Field(None, description="健康检查消息")
    timestamp: str = Field(..., description="检查时间戳（ISO格式）")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


class AdapterHealthResponse(BaseModel):
    """适配器健康状态响应模型"""
    
    adapters: Dict[str, AdapterHealthStatus] = Field(..., description="适配器健康状态字典")
    healthy_count: int = Field(..., description="健康适配器数量")
    unhealthy_count: int = Field(..., description="不健康适配器数量")
    unknown_count: int = Field(..., description="未知状态适配器数量")


class AgentTaskResponse(BaseModel):
    """Agent任务响应模型"""
    
    content: str = Field(..., description="任务执行结果")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="工具调用记录")
    iterations: int = Field(..., description="迭代次数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "北京今天晴天，温度25°C",
                "tool_calls": [
                    {
                        "tool": "get_weather",
                        "arguments": {"city": "北京"},
                        "result": "晴天，25°C"
                    }
                ],
                "iterations": 2,
                "metadata": {
                    "model": "gpt-3.5-turbo",
                    "usage": {
                        "prompt_tokens": 50,
                        "completion_tokens": 30,
                        "total_tokens": 80
                    }
                }
            }
        }


class ToolRegistrationResponse(BaseModel):
    """工具注册响应模型"""
    
    success: bool = Field(..., description="是否注册成功")
    message: str = Field(..., description="响应消息")
    tool_name: str = Field(..., description="工具名称")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "工具注册成功",
                "tool_name": "get_weather"
            }
        }


class VectorSearchResponse(BaseModel):
    """向量搜索响应模型"""
    
    results: List[Dict[str, Any]] = Field(..., description="搜索结果列表")
    count: int = Field(..., description="结果数量")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "conversation_id": "conv-123",
                        "similarity": 0.95,
                        "metadata": {}
                    }
                ],
                "count": 1
            }
        }


class MultiAgentTaskResponse(BaseModel):
    """多Agent任务响应模型"""
    
    content: str = Field(..., description="聚合后的执行结果")
    agent_results: List[Dict[str, Any]] = Field(default_factory=list, description="各Agent的执行结果")
    strategy: str = Field(..., description="使用的分配策略")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "聚合后的结果",
                "agent_results": [],
                "strategy": "round_robin",
                "metadata": {}
            }
        }


class VisionGenerateResponse(BaseModel):
    """Vision图像生成响应模型"""
    
    images: List[str] = Field(..., description="生成的图像列表（URL或base64数据）")
    model: str = Field(..., description="使用的模型名称")
    count: int = Field(..., description="生成的图像数量")
    created_at: str = Field(..., description="创建时间（ISO格式）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "images": ["https://example.com/generated-image.jpg"],
                "model": "dall-e-3",
                "count": 1,
                "created_at": "2026-01-22T10:00:00",
                "metadata": {}
            }
        }


class VisionAnalyzeResponse(BaseModel):
    """Vision图像分析响应模型"""
    
    model: str = Field(..., description="使用的模型名称")
    text: Optional[str] = Field(None, description="OCR识别的文本")
    objects: List[Dict[str, Any]] = Field(default_factory=list, description="识别的物体列表")
    description: Optional[str] = Field(None, description="图像描述")
    created_at: str = Field(..., description="创建时间（ISO格式）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-4-vision",
                "text": "识别到的文本内容",
                "objects": [],
                "description": "图像描述内容",
                "created_at": "2026-01-22T10:00:00",
                "metadata": {}
            }
        }


class VisionEditResponse(BaseModel):
    """Vision图像编辑响应模型"""
    
    images: List[str] = Field(..., description="编辑后的图像列表（URL或base64数据）")
    model: str = Field(..., description="使用的模型名称")
    count: int = Field(..., description="编辑后的图像数量")
    created_at: str = Field(..., description="创建时间（ISO格式）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "images": ["https://example.com/edited-image.jpg"],
                "model": "dall-e-2",
                "count": 1,
                "created_at": "2026-01-22T10:00:00",
                "metadata": {}
            }
        }