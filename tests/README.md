# 测试文档

## 📋 测试概述

本目录包含AI框架项目的所有测试代码。

**测试原则**：
- 每个模块都有对应的测试
- 测试覆盖率目标：80%+
- 使用pytest作为测试框架
- 所有测试必须独立运行，不依赖外部资源

---

## 📁 测试目录结构

```
tests/
├── __init__.py
├── conftest.py              # pytest配置和公共fixture
├── README.md                # 本文件
└── unit/                    # 单元测试
    ├── core/                # 核心模块测试
    │   ├── base/            # 基础类测试
    │   │   ├── test_service.py
    │   │   ├── test_adapter.py
    │   │   └── test_plugin.py
    │   └── llm/             # LLM服务测试
    │       ├── test_service.py
    │       ├── test_context.py
    │       ├── test_service_auto_register.py
    │       └── adapters/    # 适配器测试
    │           ├── test_doubao_adapter.py
    │           ├── test_qwen_adapter.py
    │           ├── test_deepseek_adapter.py
    │           └── test_registry.py
    └── infrastructure/      # 基础设施模块测试
        ├── config/          # 配置管理测试
        │   └── test_manager.py
        └── log/             # 日志管理测试
            └── test_manager.py
```

---

## 🚀 运行测试

### 安装测试依赖

```bash
pip install pytest pytest-asyncio pytest-cov
```

### 运行所有测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行指定模块的测试
pytest tests/unit/core/ -v

# 运行指定文件的测试
pytest tests/unit/core/base/test_service.py -v
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=core --cov=infrastructure --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

### 异步测试

所有异步测试都使用`@pytest.mark.asyncio`装饰器：

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

---

## 📊 测试覆盖情况

### 已覆盖的模块

#### 基础模块
- ✅ `core/base/service.py` - BaseService测试
- ✅ `core/base/adapter.py` - BaseAdapter测试
- ✅ `core/base/plugin.py` - BasePlugin测试

#### LLM服务模块
- ✅ `core/llm/service.py` - LLMService测试
- ✅ `core/llm/context.py` - ConversationContext测试
- ✅ `core/llm/models.py` - 数据模型测试（通过service测试覆盖）
- ✅ `core/llm/adapters/base.py` - BaseLLMAdapter测试
- ✅ `core/llm/adapters/registry.py` - AdapterRegistry测试
- ✅ `core/llm/adapters/doubao_adapter.py` - 豆包适配器测试
- ✅ `core/llm/adapters/qwen_adapter.py` - 千问适配器测试
- ✅ `core/llm/adapters/deepseek_adapter.py` - DeepSeek适配器测试

#### 基础设施模块
- ✅ `infrastructure/config/manager.py` - ConfigManager测试
- ✅ `infrastructure/config/loader.py` - ConfigLoader测试（通过manager测试覆盖）
- ✅ `infrastructure/config/validator.py` - ConfigValidator测试（通过manager测试覆盖）
- ✅ `infrastructure/log/manager.py` - LogManager测试

### 待测试的模块

- ⏳ `core/llm/service.py` - 与真实适配器的集成测试
- ⏳ `core/llm/adapters/*` - 与真实API的集成测试
- ⏳ 端到端测试

---

## 🧪 测试类型

### 单元测试（Unit Tests）

测试单个模块或类的功能，使用Mock隔离外部依赖。

**示例**：
```python
@pytest.mark.asyncio
async def test_service_initialization():
    config = {"test": True}
    service = MyService(config)
    await service.initialize()
    assert service.is_initialized is True
```

### 集成测试（Integration Tests）

测试多个模块之间的交互。

**示例**：
```python
@pytest.mark.asyncio
async def test_service_with_config():
    config = ConfigManager.load()
    service = MyService(config)
    await service.initialize()
    # 测试服务与配置管理器的集成
```

### 端到端测试（E2E Tests）

测试完整的业务流程。

**待实现**

---

## 🔧 测试工具和配置

### pytest配置

**conftest.py**：包含公共fixture和配置

### 公共Fixture

- `sample_config`：示例配置
- `empty_config`：空配置（用于错误测试）

### 测试约定

1. **测试文件命名**：`test_模块名.py`
2. **测试类命名**：`TestClassName`
3. **测试函数命名**：`test_功能描述()`
4. **AAA模式**：Arrange（准备）→ Act（执行）→ Assert（断言）

---

## ✅ 测试检查清单

### 编写测试时

- [ ] 测试文件命名符合规范
- [ ] 测试函数有清晰的描述性名称
- [ ] 使用AAA模式组织测试
- [ ] 异步测试使用`@pytest.mark.asyncio`
- [ ] Mock外部依赖
- [ ] 测试边界情况和错误场景
- [ ] 测试覆盖率足够（80%+）

### 运行测试前

- [ ] 确保所有依赖已安装
- [ ] 确保测试环境配置正确
- [ ] 检查测试文件没有语法错误

---

## 📝 测试示例

### 基础服务测试

```python
@pytest.mark.asyncio
async def test_service_initialization():
    """测试服务初始化"""
    # Arrange
    config = {"api_key": "test-key"}
    
    # Act
    service = MyService(config)
    await service.initialize()
    
    # Assert
    assert service.is_initialized is True
```

### 适配器测试

```python
@pytest.mark.asyncio
async def test_adapter_call():
    """测试适配器调用"""
    # Arrange
    adapter = MyAdapter({"api_key": "test-key"})
    await adapter.initialize()
    
    # Act
    response = await adapter.call(messages=[...])
    
    # Assert
    assert "content" in response
```

### Mock测试

```python
@patch("httpx.AsyncClient")
async def test_with_mock(mock_client):
    """使用Mock测试"""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "success"}
    mock_client.return_value.post = AsyncMock(return_value=mock_response)
    
    # Act
    result = await my_function()
    
    # Assert
    assert result == "success"
```

---

## 🔍 故障排查

### 常见问题

1. **pytest未安装**
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **异步测试失败**
   - 确保使用`@pytest.mark.asyncio`装饰器
   - 确保安装了`pytest-asyncio`

3. **导入错误**
   - 确保项目根目录在Python路径中
   - 检查`__init__.py`文件是否存在

4. **Mock不工作**
   - 确保Mock路径正确
   - 使用`patch`装饰器或上下文管理器

---

## 📚 相关文档

- [代码规范](../.cursor/rules/CodeStandards.mdc) → "测试规范"部分
- [项目规则](../.cursor/rules/ProjectRules.mdc) → "测试目录"部分
- [快速参考](../docs/guides/quick-reference.md) → "编写测试"部分

---

## 🔄 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-01-21 | 1.0 | 初始版本，创建测试文档 | - |
