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
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }


class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    
    messages: List[Message] = Field(..., description="消息列表", min_items=1)
    model: Optional[str] = Field(None, description="模型名称，默认使用服务默认模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制输出随机性")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7
            }
        }


class AgentTaskRequest(BaseModel):
    """Agent任务请求模型"""
    
    task: str = Field(..., description="任务描述", min_length=1)
    conversation_id: Optional[str] = Field(None, description="对话ID，用于长期记忆")
    model: Optional[str] = Field(None, description="模型名称，默认使用服务默认模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制输出随机性")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "查询北京天气",
                "conversation_id": "conv-123",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7
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