# Vision 适配器配置指南

## 配置 DALL-E 适配器

### 方法一：通过配置文件

在 `config/dev.yaml` 或 `config/default.yaml` 中添加：

```yaml
vision:
  adapters:
    dalle-adapter:
      api_key: "your-openai-api-key"  # 替换为实际的OpenAI API密钥
      base_url: "https://api.openai.com/v1"
      default_model: "dall-e-3"
```

### 方法二：通过环境变量

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

然后在配置文件中引用：
```yaml
vision:
  adapters:
    dalle-adapter:
      api_key: "${OPENAI_API_KEY}"
```

### 验证配置

配置完成后，重启后端服务，然后测试：

```bash
curl -X POST http://localhost:8000/api/v1/vision/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset"}'
```

如果配置成功，应该返回生成的图像URL。

## 注意事项

1. **API密钥安全**：不要将API密钥提交到版本控制系统
2. **费用**：DALL-E API调用会产生费用，请注意使用量
3. **模型选择**：
   - `dall-e-3`：更高质量，但只支持生成1张图像
   - `dall-e-2`：支持生成多张图像，但质量较低

## 故障排查

如果遇到 500 或 503 错误：

1. 检查API密钥是否正确配置
2. 检查网络连接是否正常
3. 查看后端日志获取详细错误信息
4. 确认适配器是否成功注册（查看日志中的"已注册适配器"信息）
