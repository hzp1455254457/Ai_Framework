"""
API请求模型模块

定义所有API请求的数据模型。
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """消息模型"""
    
    role: str = Field(..., description="消息角色：user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    
    messages: List[Message] = Field(..., description="消息列表", min_items=1)
    model: Optional[str] = Field(None, description="模型名称，默认使用服务默认模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制输出随机性")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数")
    use_agent: bool = Field(False, description="是否启用Agent模式进行工具调用")
    conversation_id: Optional[str] = Field(None, description="对话ID，用于Agent长期记忆")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000,
                "use_agent": False,
                "conversation_id": None
            }
        }


class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    
    messages: List[Message] = Field(..., description="消息列表", min_items=1)
    model: Optional[str] = Field(None, description="模型名称，默认使用服务默认模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制输出随机性")
    use_agent: bool = Field(False, description="是否启用Agent模式进行工具调用")
    conversation_id: Optional[str] = Field(None, description="对话ID，用于Agent长期记忆")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "use_agent": False,
                "conversation_id": None
            }
        }


class AgentTaskRequest(BaseModel):
    """Agent任务请求模型"""
    
    task: str = Field(..., description="任务描述", min_length=1)
    conversation_id: Optional[str] = Field(None, description="对话ID，用于长期记忆")
    model: Optional[str] = Field(None, description="模型名称，默认使用服务默认模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制输出随机性")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数")
    use_planner: bool = Field(False, description="是否使用任务规划器")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息（用于规划器）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "查询北京天气",
                "conversation_id": "conv-123",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "use_planner": False
            }
        }


class VectorSearchRequest(BaseModel):
    """向量搜索请求模型"""
    
    query: str = Field(..., description="查询文本", min_length=1)
    top_k: int = Field(5, ge=1, le=100, description="返回结果数量")
    conversation_id: Optional[str] = Field(None, description="限制搜索的对话ID（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "关于天气的对话",
                "top_k": 5
            }
        }


class MultiAgentTaskRequest(BaseModel):
    """多Agent任务请求模型"""
    
    task: str = Field(..., description="任务描述", min_length=1)
    strategy: str = Field("round_robin", description="任务分配策略：round_robin/load_balancing/specialization")
    agent_ids: Optional[List[str]] = Field(None, description="指定使用的Agent ID列表（可选）")
    conversation_id: Optional[str] = Field(None, description="对话ID")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "查询北京天气",
                "strategy": "round_robin",
                "agent_ids": ["agent1", "agent2"]
            }
        }


class ToolRegistrationRequest(BaseModel):
    """工具注册请求模型"""
    
    name: str = Field(..., description="工具名称", min_length=1)
    description: str = Field(..., description="工具描述", min_length=1)
    parameters: Dict[str, Any] = Field(..., description="工具参数schema（JSON Schema格式）")
    allow_override: bool = Field(False, description="是否允许覆盖已存在的工具")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "get_weather",
                "description": "获取城市天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "required": ["city"]
                },
                "allow_override": False
            }
        }


class VisionGenerateRequest(BaseModel):
    """Vision图像生成请求模型"""
    
    prompt: str = Field(..., description="文本提示词", min_length=1)
    size: str = Field("1024x1024", description="图像尺寸：256x256/512x512/1024x1024/1024x1792/1792x1024")
    n: int = Field(1, ge=1, le=10, description="生成图像数量")
    quality: str = Field("standard", description="图像质量：standard/hd")
    style: Optional[str] = Field(None, description="图像风格（可选）")
    adapter_name: Optional[str] = Field(None, description="适配器名称（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A beautiful sunset over the ocean",
                "size": "1024x1024",
                "n": 1,
                "quality": "standard",
                "style": None
            }
        }


class VisionAnalyzeRequest(BaseModel):
    """Vision图像分析请求模型"""
    
    image: str = Field(..., description="图像数据（URL、base64或文件路径）", min_length=1)
    analyze_type: str = Field("all", description="分析类型：ocr/object_detection/image_understanding/all")
    options: Optional[Dict[str, Any]] = Field(None, description="分析选项（可选）")
    adapter_name: Optional[str] = Field(None, description="适配器名称（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image": "https://example.com/image.jpg",
                "analyze_type": "all",
                "options": {}
            }
        }


class VisionEditRequest(BaseModel):
    """Vision图像编辑请求模型"""
    
    image: str = Field(..., description="原始图像数据（URL、base64或文件路径）", min_length=1)
    prompt: str = Field(..., description="编辑提示词", min_length=1)
    mask: Optional[str] = Field(None, description="遮罩图像（可选，指定编辑区域）")
    size: Optional[str] = Field(None, description="输出图像尺寸（可选）")
    n: int = Field(1, ge=1, le=10, description="生成图像数量")
    adapter_name: Optional[str] = Field(None, description="适配器名称（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image": "https://example.com/image.jpg",
                "prompt": "Add a rainbow in the sky",
                "mask": None,
                "size": None,
                "n": 1
            }
        }