# Design: AI框架重构 - 集成主流AI框架

## Context

当前AI框架采用自研适配器模式，每个模型提供商都需要单独实现适配器。虽然架构清晰，但随着支持的模型增多，维护成本上升，且缺少企业级功能（路由、负载均衡、成本优化等）。

主流AI框架提供了丰富的功能：
- **LiteLLM**：统一的多模型接口，支持100+模型提供商，内置路由、负载均衡、成本优化等功能
- **LangChain**：AI应用开发框架，提供链式调用、工具集成、记忆管理、文档处理等能力
- **LangGraph**：基于LangChain的工作流编排框架，支持复杂的状态机和工作流定义

虽然这些框架功能强大，但完全替换现有架构风险较大。采用可选集成策略，用户可以根据需求选择使用哪些框架，保持架构灵活性。

## Goals / Non-Goals

### Goals

1. **集成主流AI框架**：
   - 集成LiteLLM作为可选统一接口层，支持更多模型提供商
   - 集成LangChain作为可选AI应用开发框架，提供链式调用、工具集成等能力
   - 集成LangGraph作为可选工作流编排引擎，支持复杂工作流
2. **保持架构灵活性**：支持多种模式组合，用户可根据需求选择
3. **增强企业级功能**：实现路由、负载均衡、成本优化、监控、工作流编排等功能
4. **提升性能和可扩展性**：优化关键路径，支持插件式扩展
5. **保持向后兼容**：现有代码和配置无需修改即可使用

### Non-Goals

1. **不强制使用任何框架**：所有框架都是可选的，自研实现继续可用
2. **不改变现有API**：保持现有API接口不变，新功能通过配置启用
3. **不改变项目定位**：保持个人开发者友好的轻量级定位，框架集成是可选的
4. **不完全依赖外部框架**：保持核心功能的自研实现，框架作为增强能力

## Decisions

### Decision 1: 采用适配器路由层架构

**What**: 在LLMService和适配器之间增加路由层，支持LiteLLM和自研适配器两种模式。

**Why**: 
- 保持架构灵活性，用户可以选择使用LiteLLM或自研适配器
- 向后兼容，现有适配器无需修改
- 支持渐进式迁移，可以逐步迁移到新架构

**Alternatives considered**:
- **完全替换为LiteLLM**: 风险大，失去对架构的控制
- **保持现状**: 无法获得LiteLLM的优势，维护成本高
- **并行实现**: 代码重复，维护成本高

**Trade-offs**:
- ✅ 灵活性高，支持两种模式
- ✅ 向后兼容，风险低
- ⚠️ 增加了一层抽象，可能带来性能开销（通过优化缓解）

### Decision 2: 使用工厂模式创建适配器

**What**: 引入适配器工厂，根据配置动态创建适配器实例。

**Why**:
- 符合开闭原则，新增适配器无需修改核心代码
- 支持插件式扩展，可以动态加载适配器
- 统一适配器创建逻辑，便于管理和测试

**Alternatives considered**:
- **直接实例化**: 代码耦合，难以扩展
- **依赖注入**: 过于复杂，不符合项目定位

**Trade-offs**:
- ✅ 扩展性好，符合开闭原则
- ✅ 代码解耦，易于测试
- ⚠️ 增加了一层抽象（但收益大于成本）

### Decision 3: 实现智能路由策略

**What**: 根据模型能力标签、成本、性能、可用性等因素智能选择模型。

**Why**:
- 提升用户体验，自动选择最适合的模型
- 优化成本，在满足需求的前提下选择成本最低的模型
- 提高可用性，自动故障转移

**Alternatives considered**:
- **固定模型**: 灵活性差，无法优化
- **手动选择**: 用户体验差，需要了解所有模型

**Trade-offs**:
- ✅ 用户体验好，自动优化
- ✅ 成本可控，性能优化
- ⚠️ 路由逻辑复杂，需要充分测试

### Decision 4: LiteLLM作为可选依赖

**What**: LiteLLM作为可选依赖，不强制安装。

**Why**:
- 保持项目轻量级定位，不增加不必要的依赖
- 用户可以选择是否使用LiteLLM
- 降低依赖冲突风险

**Alternatives considered**:
- **必需依赖**: 增加项目重量，可能带来依赖冲突
- **完全自研**: 无法获得LiteLLM的优势

**Trade-offs**:
- ✅ 灵活性高，用户可选择
- ✅ 保持轻量级定位
- ⚠️ 需要处理可选依赖的兼容性

### Decision 7: 性能优化策略

**What**: 实现HTTP连接池、批量处理、请求缓存等性能优化。

**Why**:
- 提升响应速度，改善用户体验
- 降低资源消耗，提高并发能力
- 优化成本，减少重复请求

**Alternatives considered**:
- **不优化**: 性能差，用户体验差
- **过度优化**: 增加复杂度，维护成本高

**Trade-offs**:
- ✅ 性能提升明显
- ✅ 用户体验改善
- ⚠️ 实现复杂度增加（但收益大于成本）

### Decision 8: 框架选择指导原则

**What**: 提供清晰的框架选择指导，帮助用户根据场景选择合适的框架。

**Why**:
- 不同场景适合不同的框架组合
- 避免用户过度使用复杂框架导致性能问题
- 帮助用户做出最佳选择

**选择建议**:
- **简单对话场景**: 使用自研适配器或LiteLLM
- **需要链式调用**: 使用LangChain
- **需要复杂工作流**: 使用LangGraph
- **需要多模型路由**: 使用LiteLLM
- **需要成本优化**: 使用LiteLLM + 自研路由

**Trade-offs**:
- ✅ 帮助用户做出最佳选择
- ✅ 避免过度设计
- ⚠️ 需要维护选择指南文档

## Architecture Design

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   应用层 (Application Layer)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Web UI   │  │ CLI      │  │ API      │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                核心服务层 (Core Service Layer)            │
│  ┌──────────────────────────────────────────────────┐   │
│  │            LLMService (重构)                      │   │
│  │  - 统一接口                                       │   │
│  │  - 路由决策                                       │   │
│  │  - 负载均衡                                       │   │
│  │  - 成本优化                                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              适配器路由层 (Adapter Router Layer)         │
│  ┌──────────────────────────────────────────────────┐   │
│  │         AdapterRouter                             │   │
│  │  - 路由策略（成本/性能/可用性）                    │   │
│  │  - 负载均衡                                       │   │
│  │  - 故障转移                                       │   │
│  └──────────────────────────────────────────────────┘   │
│                           ↓                               │
│  ┌──────────────┐              ┌──────────────┐         │
│  │ LiteLLM统一  │              │ 自研适配器    │         │
│  │ 接口层       │              │ 层            │         │
│  └──────────────┘              └──────────────┘         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                适配器层 (Adapter Layer)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ LiteLLM  │  │ OpenAI   │  │ Claude   │             │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                模型提供商 (Model Providers)               │
│  OpenAI / Anthropic / Local Models / ...                │
└─────────────────────────────────────────────────────────┘
```

### 核心模块设计

#### 1. AdapterRouter (适配器路由层)

**职责**：
- 根据路由策略选择适配器
- 实现负载均衡和故障转移
- 管理适配器健康状态

**接口设计**：
```python
class AdapterRouter:
    async def route(
        self,
        request: LLMRequest,
        strategy: RoutingStrategy
    ) -> BaseLLMAdapter:
        """根据策略路由到合适的适配器"""
        pass
    
    async def get_healthy_adapters(
        self,
        capability: ModelCapability
    ) -> List[BaseLLMAdapter]:
        """获取健康的适配器列表"""
        pass
```

#### 2. AdapterFactory (适配器工厂)

**职责**：
- 根据配置创建适配器实例
- 支持动态注册适配器
- 管理适配器生命周期

**接口设计**：
```python
class AdapterFactory:
    def create_adapter(
        self,
        adapter_type: str,
        config: Dict[str, Any]
    ) -> BaseLLMAdapter:
        """创建适配器实例"""
        pass
    
    def register_adapter(
        self,
        adapter_type: str,
        adapter_class: Type[BaseLLMAdapter]
    ) -> None:
        """注册适配器类"""
        pass
```

#### 3. RoutingStrategy (路由策略)

**职责**：
- 定义路由策略接口
- 实现多种路由策略（成本优先、性能优先、可用性优先等）

**接口设计**：
```python
class RoutingStrategy(ABC):
    @abstractmethod
    async def select_adapter(
        self,
        request: LLMRequest,
        adapters: List[BaseLLMAdapter]
    ) -> BaseLLMAdapter:
        """选择适配器"""
        pass
```

#### 4. LiteLLMAdapter (LiteLLM适配器包装)

**职责**：
- 包装LiteLLM，实现BaseLLMAdapter接口
- 提供统一接口，屏蔽LiteLLM细节

**接口设计**：
```python
class LiteLLMAdapter(BaseLLMAdapter):
    """LiteLLM适配器包装"""
    async def call(self, ...) -> Dict[str, Any]:
        # 调用LiteLLM，转换为统一格式
        pass
```

#### 5. LangChainIntegration (LangChain集成层)

**职责**：
- 集成LangChain的链式调用能力
- 提供LangChain兼容的接口
- 支持LangChain的工具和记忆管理

**接口设计**：
```python
class LangChainIntegration:
    """LangChain集成层"""
    def create_chain(self, chain_type: str, config: Dict) -> Chain:
        """创建LangChain链"""
        pass
    
    def add_tool(self, tool: Tool) -> None:
        """添加LangChain工具"""
        pass
    
    async def run_chain(self, chain: Chain, input: Dict) -> Dict:
        """运行LangChain链"""
        pass
```

#### 6. LangGraphIntegration (LangGraph集成层)

**职责**：
- 集成LangGraph的工作流编排能力
- 支持复杂的状态机和工作流定义
- 提供工作流执行和状态管理

**接口设计**：
```python
class LangGraphIntegration:
    """LangGraph集成层"""
    def create_workflow(self, workflow_def: Dict) -> StateGraph:
        """创建工作流"""
        pass
    
    async def run_workflow(
        self,
        workflow: StateGraph,
        initial_state: Dict
    ) -> Dict:
        """运行工作流"""
        pass
    
    def visualize_workflow(self, workflow: StateGraph) -> str:
        """可视化工作流（可选）"""
        pass
```

#### 7. PerformanceOptimizer (性能优化器)

**职责**：
- HTTP连接池管理
- 批量请求处理
- 请求缓存和去重

**接口设计**：
```python
class PerformanceOptimizer:
    async def optimize_request(
        self,
        request: LLMRequest
    ) -> LLMRequest:
        """优化请求（缓存、去重等）"""
        pass
    
    def get_connection_pool(
        self,
        adapter: BaseLLMAdapter
    ) -> ConnectionPool:
        """获取连接池"""
        pass
```

#### 6. CostManager (成本管理器)

**职责**：
- Token使用统计
- 成本计算和预算管理
- 成本优化建议

**接口设计**：
```python
class CostManager:
    async def calculate_cost(
        self,
        usage: TokenUsage,
        model: str
    ) -> float:
        """计算成本"""
        pass
    
    async def check_budget(
        self,
        cost: float
    ) -> bool:
        """检查预算"""
        pass
```

#### 7. Monitor (监控器)

**职责**：
- Prometheus指标采集
- 请求追踪
- 性能分析

**接口设计**：
```python
class Monitor:
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict[str, str]
    ) -> None:
        """记录指标"""
        pass
    
    def trace_request(
        self,
        request_id: str,
        span: Span
    ) -> None:
        """追踪请求"""
        pass
```

### 数据模型设计

#### ModelCapability (模型能力标签)

```python
@dataclass
class ModelCapability:
    """模型能力标签"""
    reasoning: bool = False      # 推理能力
    creativity: bool = False     # 创造力
    cost_effective: bool = False # 成本效益
    fast: bool = False          # 快速响应
    multilingual: bool = False  # 多语言支持
```

#### RoutingStrategy (路由策略枚举)

```python
class RoutingStrategy(Enum):
    COST_FIRST = "cost_first"           # 成本优先
    PERFORMANCE_FIRST = "performance_first"  # 性能优先
    AVAILABILITY_FIRST = "availability_first"  # 可用性优先
    BALANCED = "balanced"               # 平衡模式
```

#### LLMRequest (LLM请求模型)

```python
@dataclass
class LLMRequest:
    """LLM请求模型"""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    capability_requirements: Optional[ModelCapability] = None
    budget: Optional[float] = None
```

## Risks / Trade-offs

### 风险1: 架构复杂度增加

**风险**: 新增路由层和工厂模式可能增加架构复杂度。

**缓解**:
- 清晰的模块划分，单一职责原则
- 详细的文档和代码注释
- 充分的单元测试和集成测试

### 风险2: 性能开销

**风险**: 新增抽象层可能带来性能开销。

**缓解**:
- 性能基准测试，确保关键路径性能不下降
- 优化关键路径，减少不必要的抽象
- 使用缓存和连接池优化性能

### 风险3: 依赖冲突

**风险**: LiteLLM可能与其他依赖冲突。

**缓解**:
- LiteLLM作为可选依赖，不强制安装
- 提供fallback机制，LiteLLM不可用时使用自研适配器
- 版本锁定，避免依赖冲突

### 风险4: 向后兼容性

**风险**: 重构可能破坏现有功能。

**缓解**:
- 保持API接口不变
- 保持配置兼容
- 充分的回归测试
- 渐进式迁移策略

## Migration Plan

### 阶段1: 基础架构重构（2-3周）

1. 实现适配器工厂和注册表
2. 重构适配器基类，增强接口
3. 实现适配器路由层基础功能
4. 保持向后兼容，现有适配器继续工作

### 阶段2: LiteLLM集成（1-2周）

1. 实现LiteLLMAdapter包装
2. 集成LiteLLM到路由层
3. 添加配置支持LiteLLM模式
4. 编写集成测试

### 阶段3: 企业级功能（2-3周）

1. 实现智能路由策略
2. 实现负载均衡和故障转移
3. 实现成本管理和优化
4. 实现性能优化（连接池、缓存等）

### 阶段4: 监控和可观测性（1-2周）

1. 集成Prometheus指标采集
2. 实现请求追踪
3. 实现结构化日志
4. 创建监控仪表板

### 阶段5: 测试和文档（1-2周）

1. 编写完整的单元测试和集成测试
2. 性能基准测试
3. 更新架构文档
4. 创建迁移指南
5. 更新API文档

### 回滚计划

如果重构出现问题，可以：
1. 通过配置禁用新功能，回退到旧架构
2. 保持旧代码可用，支持快速回滚
3. 分阶段发布，每阶段都可以独立回滚

## Open Questions

1. **LiteLLM版本选择**: 使用哪个版本的LiteLLM？是否需要锁定版本？
2. **性能基准**: 如何定义性能基准？关键路径的性能目标是什么？
3. **成本计算**: 如何准确计算不同模型的成本？是否需要实时价格API？
4. **监控指标**: 需要采集哪些关键指标？如何定义SLA？
5. **迁移策略**: 如何帮助用户平滑迁移？是否需要自动迁移工具？
