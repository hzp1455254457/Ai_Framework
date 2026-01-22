"""
Agent路由模块

提供Agent服务相关的API接口。
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from api.models.request import (
    AgentTaskRequest,
    ToolRegistrationRequest,
    VectorSearchRequest,
    MultiAgentTaskRequest,
)
from api.models.response import (
    AgentTaskResponse,
    ToolRegistrationResponse,
    VectorSearchResponse,
    MultiAgentTaskResponse,
    ErrorResponse,
)
from api.dependencies import get_agent_engine, get_agent_orchestrator
from core.agent.engine import AgentEngine, AgentError
from core.agent.tools import Tool, ToolError
from core.agent.collaboration import AgentOrchestrator, DistributionStrategy, CollaborationError

router = APIRouter()


@router.post("/task", response_model=AgentTaskResponse)
async def run_task(
    request: AgentTaskRequest,
    agent_engine: AgentEngine = Depends(get_agent_engine),
) -> AgentTaskResponse:
    """
    Agent任务执行接口
    
    接收任务描述，执行Agent工作流，返回执行结果。
    
    参数:
        request: 任务请求，包含任务描述、对话ID等参数
        agent_engine: Agent引擎实例（依赖注入）
    
    返回:
        任务执行响应，包含执行结果、工具调用记录等
    
    异常:
        HTTPException: 请求失败时抛出
    """
    try:
        # 调用Agent引擎执行任务
        result = await agent_engine.run_task(
            task=request.task,
            conversation_id=request.conversation_id,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            context=request.context,
        )
        
        # 构建响应
        return AgentTaskResponse(
            content=result["content"],
            tool_calls=result.get("tool_calls", []),
            iterations=result.get("iterations", 1),
            metadata=result.get("metadata", {}),
        )
    
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务执行失败: {str(e)}",
        ) from e


@router.post("/tools/register", response_model=ToolRegistrationResponse)
async def register_tool(
    request: ToolRegistrationRequest,
    agent_engine: AgentEngine = Depends(get_agent_engine),
) -> ToolRegistrationResponse:
    """
    工具注册接口
    
    在运行时注册新工具，扩展Agent能力。
    
    参数:
        request: 工具注册请求，包含工具定义
        agent_engine: Agent引擎实例（依赖注入）
    
    返回:
        工具注册响应，包含注册结果
    
    异常:
        HTTPException: 注册失败时抛出
    
    注意:
        - 工具执行函数需要在服务端预先定义
        - 当前版本仅支持注册已存在的工具函数
        - 未来版本可能支持动态工具函数注册
    """
    try:
        # 注意：当前实现中，工具的执行函数需要在服务端预先定义
        # 这里仅做工具定义的验证和注册，实际执行函数需要预先注册
        # 未来可以扩展为支持动态函数注册（需要安全考虑）
        
        # 验证工具定义
        if not request.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工具名称不能为空",
            )
        
        if not request.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工具描述不能为空",
            )
        
        if not isinstance(request.parameters, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工具参数必须是字典格式（JSON Schema）",
            )
        
        # 检查工具是否已存在
        if agent_engine.get_tools() and request.name in agent_engine.get_tools():
            if not request.allow_override:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"工具已存在: {request.name}，如需覆盖请设置 allow_override=True",
                )
        
        # 注意：当前实现中，工具的执行函数需要预先在服务端定义
        # 这里仅做工具定义的注册，实际执行需要预先注册工具函数
        # 返回成功响应（实际工具注册需要在服务端预先完成）
        
        return ToolRegistrationResponse(
            success=True,
            message=f"工具定义已接收: {request.name}（注意：执行函数需要在服务端预先定义）",
            tool_name=request.name,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"工具注册失败: {str(e)}",
        ) from e


@router.get("/tools", response_model=Dict[str, Any])
async def list_tools(
    agent_engine: AgentEngine = Depends(get_agent_engine),
) -> Dict[str, Any]:
    """
    获取已注册的工具列表
    
    参数:
        agent_engine: Agent引擎实例（依赖注入）
    
    返回:
        工具列表，包含工具名称和schema
    """
    try:
        tools = agent_engine.get_tools()
        tool_schemas = agent_engine.get_tool_schemas()
        
        return {
            "tools": tools,
            "schemas": tool_schemas,
            "count": len(tools),
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工具列表失败: {str(e)}",
        ) from e


@router.post("/memory/search", response_model=VectorSearchResponse)
async def search_memory(
    request: VectorSearchRequest,
    agent_engine: AgentEngine = Depends(get_agent_engine),
) -> VectorSearchResponse:
    """
    向量语义搜索接口
    
    在长期记忆中根据语义相似度搜索相关对话历史。
    
    参数:
        request: 搜索请求
        agent_engine: Agent引擎实例（依赖注入）
    
    返回:
        搜索结果响应
    
    异常:
        HTTPException: 搜索失败时抛出
    
    注意:
        需要先配置向量后端才能使用此功能
    """
    try:
        if not agent_engine._long_term_memory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="长期记忆未启用，无法进行语义搜索",
            )
        
        # 执行语义搜索
        results = await agent_engine._long_term_memory.search_by_semantics(
            query=request.query,
            top_k=request.top_k,
        )
        
        return VectorSearchResponse(
            results=results,
            count=len(results),
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语义搜索失败: {str(e)}",
        ) from e


@router.post("/collaboration/task", response_model=MultiAgentTaskResponse)
async def execute_multi_agent_task(
    request: MultiAgentTaskRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
) -> MultiAgentTaskResponse:
    """
    多Agent协作任务执行接口
    
    使用多个Agent协同执行任务。
    
    参数:
        request: 多Agent任务请求
        orchestrator: Agent编排器实例（依赖注入）
    
    返回:
        多Agent任务响应
    
    异常:
        HTTPException: 执行失败时抛出
    """
    try:
        # 设置分配策略
        try:
            strategy = DistributionStrategy(request.strategy)
            orchestrator.set_strategy(strategy)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的分配策略: {request.strategy}",
            )
        
        # 执行任务
        result = await orchestrator.execute_task(
            task=request.task,
            conversation_id=request.conversation_id,
            model=request.model,
            temperature=request.temperature,
        )
        
        return MultiAgentTaskResponse(
            content=result.get("content", ""),
            agent_results=[result],
            strategy=request.strategy,
            metadata=result.get("metadata", {}),
        )
    
    except CollaborationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"多Agent任务执行失败: {str(e)}",
        ) from e


@router.get("/collaboration/status", response_model=Dict[str, Any])
async def get_collaboration_status(
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
) -> Dict[str, Any]:
    """
    获取多Agent协作状态
    
    参数:
        orchestrator: Agent编排器实例（依赖注入）
    
    返回:
        协作状态信息
    """
    try:
        agents_status = orchestrator.get_agent_status()
        return {
            "agents": agents_status,
            "strategy": orchestrator._strategy_type.value,
            "total_agents": len(agents_status),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取协作状态失败: {str(e)}",
        ) from e
