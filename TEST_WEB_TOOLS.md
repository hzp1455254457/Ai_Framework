# 互联网访问工具测试指南

## 1. 启动服务器

### 方式1：使用 uvicorn 命令（推荐）
```bash
cd F:\Ai_Framework
python -m uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

### 方式2：使用 Python 直接运行
```bash
cd F:\Ai_Framework
python -m api.fastapi_app
```

## 2. 验证服务器启动

### 检查健康状态
```bash
curl http://localhost:8000/api/v1/health
```

或使用浏览器访问：
- http://localhost:8000/
- http://localhost:8000/docs (Swagger UI)

## 3. 测试互联网工具注册

### 检查工具列表
```bash
curl http://localhost:8000/api/v1/agent/tools
```

或使用 Python：
```python
import requests
response = requests.get('http://localhost:8000/api/v1/agent/tools')
print(response.json())
```

**预期结果**：应该看到 `web_search` 和 `fetch_webpage` 工具在列表中。

## 4. 测试 web_search 工具

### 方式1：直接调用工具函数
```python
import asyncio
from core.agent.tools.web_tools import web_search

async def test():
    result = await web_search(
        query="Python async programming",
        max_results=3,
        search_engine="duckduckgo",
        timeout=15.0
    )
    print(result)

asyncio.run(test())
```

### 方式2：通过 Agent API 调用
```bash
curl -X POST http://localhost:8000/api/v1/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "使用web_search工具搜索Python异步编程的最新信息，返回前3个结果"
  }'
```

或使用 Python：
```python
import requests
import json

response = requests.post(
    'http://localhost:8000/api/v1/agent/task',
    json={
        'task': '使用web_search工具搜索Python异步编程的最新信息'
    },
    timeout=60
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

## 5. 测试 fetch_webpage 工具

### 方式1：直接调用工具函数
```python
import asyncio
from core.agent.tools.web_tools import fetch_webpage

async def test():
    result = await fetch_webpage(
        url="https://www.python.org",
        timeout=15.0,
        max_length=1000
    )
    print(result[:500])  # 打印前500字符

asyncio.run(test())
```

### 方式2：通过 Agent API 调用
```bash
curl -X POST http://localhost:8000/api/v1/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "使用fetch_webpage工具获取https://www.python.org的内容"
  }'
```

## 6. 配置检查

确保 `config/default.yaml` 中互联网工具已启用：

```yaml
agent:
  web_tools:
    enabled: true  # 必须为 true
    web_search:
      enabled: true
      search_engine: "duckduckgo"
    fetch_webpage:
      enabled: true
```

## 7. 依赖检查

确保已安装所需依赖：

```bash
pip install httpx beautifulsoup4
```

或安装所有依赖：

```bash
pip install -r requirements.txt
```

## 8. 常见问题

### 问题1：工具未注册
**原因**：配置中 `web_tools.enabled` 为 `false` 或服务器未重启
**解决**：检查配置并重启服务器

### 问题2：网络请求失败
**原因**：网络连接问题或超时设置过短
**解决**：检查网络连接，增加 `timeout` 配置

### 问题3：BeautifulSoup 导入失败
**原因**：未安装 `beautifulsoup4`
**解决**：运行 `pip install beautifulsoup4`

### 问题4：服务器启动失败
**原因**：端口被占用或依赖缺失
**解决**：
- 检查端口占用：`netstat -ano | findstr ":8000"`
- 安装依赖：`pip install -r requirements.txt`

## 9. 测试脚本

运行完整测试：

```bash
python test_web_tools.py
```

或运行简单测试：

```bash
python test_simple.py
```

## 10. 验证清单

- [ ] 服务器成功启动（端口8000）
- [ ] 健康检查接口返回 200
- [ ] `/api/v1/agent/tools` 返回工具列表，包含 `web_search` 和 `fetch_webpage`
- [ ] `web_search` 工具可以成功搜索并返回结果
- [ ] `fetch_webpage` 工具可以成功获取网页内容
- [ ] Agent 可以通过 API 调用互联网工具
