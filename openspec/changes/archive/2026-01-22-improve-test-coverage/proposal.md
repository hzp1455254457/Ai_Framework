# Change: Improve Test Coverage to 80%+

## Why

当前测试覆盖率为76%，接近但未达到80%+的目标。根据测试结果报告，以下模块覆盖率较低：

1. **LLM适配器模块**：覆盖率47-50%，主要缺少：
   - 流式响应测试场景
   - 错误处理和异常场景测试
   - 边界条件测试
   - 参数验证测试

2. **配置加载器模块**：覆盖率56%，主要缺少：
   - 环境变量加载测试
   - 配置文件格式错误处理测试
   - 嵌套配置解析测试

3. **新适配器测试**：OpenAI、Claude、Ollama适配器已有基础测试，但需要补充：
   - 流式响应测试
   - 错误处理测试
   - 边界条件测试

提高测试覆盖率到80%+能够：
- 提升代码质量和稳定性
- 减少生产环境bug
- 增强代码重构信心
- 符合项目计划中的P1优先级要求

## What Changes

- 改进 `test-coverage` capability：将总体测试覆盖率从76%提升到80%+
- 重点改进以下模块的测试覆盖率：
  - `core/llm/adapters/deepseek_adapter.py`: 49% → 80%+
  - `core/llm/adapters/doubao_adapter.py`: 50% → 80%+
  - `core/llm/adapters/qwen_adapter.py`: 47% → 80%+
  - `infrastructure/config/loader.py`: 56% → 80%+
  - `core/llm/adapters/openai_adapter.py`: 补充完整测试
  - `core/llm/adapters/claude_adapter.py`: 补充流式和错误处理测试
  - `core/llm/adapters/ollama_adapter.py`: 补充流式和错误处理测试

## Impact

- **Affected specs**: `test-coverage`（本次改进）
- **Affected code (planned)**:
  - `tests/unit/core/llm/adapters/test_deepseek_adapter.py`: 补充流式响应、错误处理、边界条件测试
  - `tests/unit/core/llm/adapters/test_doubao_adapter.py`: 补充流式响应、错误处理、边界条件测试
  - `tests/unit/core/llm/adapters/test_qwen_adapter.py`: 补充流式响应、错误处理、边界条件测试
  - `tests/unit/core/llm/adapters/test_openai_adapter.py`: 补充流式响应、错误处理、边界条件测试
  - `tests/unit/core/llm/adapters/test_claude_adapter.py`: 补充流式响应、错误处理、边界条件测试
  - `tests/unit/core/llm/adapters/test_ollama_adapter.py`: 补充流式响应、错误处理、边界条件测试
  - `tests/unit/infrastructure/config/test_loader.py`: 新建测试文件，补充环境变量、配置文件格式、嵌套配置测试
  - `tests/TEST_RESULTS.md`: 更新测试结果报告

## Non-Goals

- 不在本次 change 中实现性能测试（P2优先级，后续实现）
- 不在本次 change 中实现真实API集成测试（P3优先级，可选）
- 不在本次 change 中实现端到端测试的扩展（已有基础端到端测试）
- 不在本次 change 中修改源代码（仅添加测试代码）
