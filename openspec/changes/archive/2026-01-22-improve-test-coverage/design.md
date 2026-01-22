# Design: Improve Test Coverage to 80%+

## 技术设计

### 测试策略

#### 1. 适配器测试改进策略

**目标**：将适配器测试覆盖率从47-50%提升到80%+

**测试场景补充**：

1. **流式响应测试**
   - 测试SSE格式解析（Claude）
   - 测试JSON Lines格式解析（Ollama）
   - 测试流式响应中断处理
   - 测试流式响应错误处理

2. **错误处理测试**
   - HTTP错误状态码（400, 401, 403, 429, 500）
   - 网络超时错误
   - 响应格式错误
   - API密钥无效错误

3. **边界条件测试**
   - 空消息列表
   - 超长消息内容
   - 无效模型名称
   - 无效参数值（temperature < 0, max_tokens < 0）

4. **参数验证测试**
   - 必需参数缺失
   - 参数类型错误
   - 参数范围验证

**实现方式**：
- 使用`unittest.mock`和`pytest`进行Mock测试
- 使用`@patch`装饰器Mock `httpx.AsyncClient`
- 创建测试fixture复用Mock设置

#### 2. 配置加载器测试改进策略

**目标**：将配置加载器测试覆盖率从56%提升到80%+

**测试场景补充**：

1. **环境变量加载测试**
   - 测试`load_environment_variables`方法
   - 测试环境变量前缀过滤
   - 测试环境变量类型转换
   - 测试环境变量缺失处理

2. **配置文件格式测试**
   - YAML格式错误处理
   - JSON格式错误处理
   - 文件不存在处理
   - 文件权限错误处理

3. **嵌套配置解析测试**
   - 深层嵌套配置访问
   - 配置合并逻辑
   - 配置覆盖优先级

**实现方式**：
- 使用临时文件和目录进行文件操作测试
- 使用`pytest.fixture`创建测试环境
- 使用`os.environ`设置和清理环境变量

### 测试文件组织

```
tests/
├── unit/
│   ├── core/
│   │   └── llm/
│   │       └── adapters/
│   │           ├── test_deepseek_adapter.py  # 扩展测试
│   │           ├── test_doubao_adapter.py   # 扩展测试
│   │           ├── test_qwen_adapter.py     # 扩展测试
│   │           ├── test_openai_adapter.py   # 扩展测试
│   │           ├── test_claude_adapter.py    # 扩展测试
│   │           └── test_ollama_adapter.py   # 扩展测试
│   └── infrastructure/
│       └── config/
│           └── test_loader.py               # 新建测试文件
```

### Mock策略

#### 适配器Mock策略

```python
@patch("httpx.AsyncClient")
async def test_stream_call_success(mock_client_class):
    """测试流式调用成功"""
    # Mock流式响应
    mock_stream = AsyncMock()
    mock_stream.__aiter__ = AsyncMock(return_value=iter([
        b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
        b'data: {"choices": [{"delta": {"content": " World"}}]}\n\n',
        b'data: [DONE]\n\n'
    ]))
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.aiter_bytes = AsyncMock(return_value=mock_stream)
    
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client_class.return_value = mock_client
    
    # 测试代码...
```

#### 配置加载器Mock策略

```python
@pytest.fixture
def temp_config_dir(tmp_path):
    """创建临时配置目录"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock环境变量"""
    monkeypatch.setenv("AI_FRAMEWORK_API_KEY", "test-key")
    monkeypatch.setenv("AI_FRAMEWORK_BASE_URL", "http://test.com")
    yield
    monkeypatch.delenv("AI_FRAMEWORK_API_KEY", raising=False)
    monkeypatch.delenv("AI_FRAMEWORK_BASE_URL", raising=False)
```

### 测试覆盖率目标

| 模块 | 当前覆盖率 | 目标覆盖率 | 改进策略 |
|------|-----------|-----------|---------|
| `deepseek_adapter.py` | 49% | 80%+ | 补充流式、错误处理、边界条件测试 |
| `doubao_adapter.py` | 50% | 80%+ | 补充流式、错误处理、边界条件测试 |
| `qwen_adapter.py` | 47% | 80%+ | 补充流式、错误处理、边界条件测试 |
| `openai_adapter.py` | 待确认 | 80%+ | 补充完整测试套件 |
| `claude_adapter.py` | 待确认 | 80%+ | 补充流式和错误处理测试 |
| `ollama_adapter.py` | 待确认 | 80%+ | 补充流式和错误处理测试 |
| `config/loader.py` | 56% | 80%+ | 新建测试文件，补充环境变量和文件格式测试 |

### 架构决策

1. **使用Mock而非真实API**：避免依赖外部服务，提高测试速度和稳定性
2. **测试文件与源代码结构一致**：便于维护和查找
3. **使用pytest fixture**：复用测试设置，减少重复代码
4. **测试命名规范**：`test_功能描述_场景描述`格式

### 依赖关系

- **pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 覆盖率统计
- **unittest.mock**: Mock功能
- **httpx**: HTTP客户端（被Mock）

### 测试执行

```bash
# 运行所有测试并查看覆盖率
pytest tests/ --cov=core --cov=infrastructure --cov-report=term-missing

# 运行特定模块测试
pytest tests/unit/core/llm/adapters/ -v

# 生成HTML覆盖率报告
pytest tests/ --cov=core --cov=infrastructure --cov-report=html
```
