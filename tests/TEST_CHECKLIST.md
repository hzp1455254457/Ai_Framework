# 测试检查清单

## 📋 测试前检查

### 环境检查

- [ ] Python版本 >= 3.10
- [ ] 已安装pytest: `pip install pytest pytest-asyncio pytest-cov`
- [ ] 已安装项目依赖: `pip install -r requirements.txt`
- [ ] 虚拟环境已激活（如使用）

### 测试文件检查

- [ ] 所有测试文件以`test_`开头
- [ ] 所有测试类以`Test`开头
- [ ] 所有测试函数以`test_`开头
- [ ] 异步测试使用`@pytest.mark.asyncio`装饰器

---

## ✅ 测试覆盖检查

### 基础模块（core/base/）

- [x] BaseService - 初始化和清理
- [x] BaseService - 配置管理
- [x] BaseService - 日志管理
- [x] BaseService - 异步上下文管理器
- [x] BaseAdapter - 初始化和清理
- [x] BaseAdapter - 适配器调用
- [x] BaseAdapter - 流式调用
- [x] BasePlugin - 初始化和清理
- [x] BasePlugin - 插件执行
- [x] BasePlugin - 依赖管理

### LLM服务模块（core/llm/）

- [x] LLMService - 服务初始化
- [x] LLMService - 适配器注册
- [x] LLMService - 聊天功能
- [x] LLMService - 流式聊天
- [x] LLMService - Token计算
- [x] ConversationContext - 消息管理
- [x] ConversationContext - 上下文清理
- [x] ConversationContext - 最大消息数限制
- [x] 自动发现和注册机制

### 适配器模块（core/llm/adapters/）

- [x] AdapterRegistry - 适配器发现
- [x] AdapterRegistry - 适配器创建
- [x] AdapterRegistry - 模型映射
- [x] DoubaoAdapter - 初始化
- [x] DoubaoAdapter - API调用（Mock）
- [x] QwenAdapter - 初始化
- [x] QwenAdapter - API调用（Mock）
- [x] DeepSeekAdapter - 初始化
- [x] DeepSeekAdapter - API调用（Mock）

### 基础设施模块（infrastructure/）

- [x] ConfigManager - 配置加载
- [x] ConfigManager - 配置访问
- [x] ConfigManager - 配置设置
- [x] ConfigManager - 配置重载
- [x] LogManager - 日志记录器创建
- [x] LogManager - 日志级别配置
- [x] LogManager - 文件日志输出
- [x] LogManager - 日志系统关闭

---

## 🐛 已知问题

### 待修复

1. 无（所有测试代码已实现）

### 待改进

1. 添加真实API集成测试（可选）
2. 添加性能基准测试
3. 添加端到端测试

---

## 📊 测试执行状态

### 最后执行时间

- **日期**：待执行
- **测试数量**：72个
- **通过数量**：待执行
- **失败数量**：待执行
- **跳过数量**：待执行

### 覆盖率目标

- **目标覆盖率**：80%+
- **当前覆盖率**：待执行测试后确定

---

## 🔧 快速测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行并查看覆盖率
pytest tests/ --cov=core --cov=infrastructure --cov-report=term

# 运行特定模块测试
pytest tests/unit/core/ -v
pytest tests/unit/infrastructure/ -v

# 运行并生成HTML覆盖率报告
pytest tests/ --cov=core --cov=infrastructure --cov-report=html
# 然后打开 htmlcov/index.html 查看报告
```
