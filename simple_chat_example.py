"""
简单聊天示例脚本
功能描述：演示如何使用AI框架进行简单的问答对话
使用方法：python simple_chat_example.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from infrastructure.config import ConfigManager
from core.llm.service import LLMService


async def main():
    """主函数：演示简单的问答对话"""
    
    print("=" * 60)
    print("AI框架简单聊天示例")
    print("=" * 60)
    print()
    
    try:
        # 1. 加载配置
        print("📋 正在加载配置...")
        config_manager = ConfigManager.load(env="dev")
        config = config_manager.config
        
        # 检查API密钥是否配置
        qwen_api_key = config.get("llm", {}).get("adapters", {}).get("qwen-adapter", {}).get("api_key", "")
        deepseek_api_key = config.get("llm", {}).get("adapters", {}).get("deepseek-adapter", {}).get("api_key", "")
        
        if not qwen_api_key and not deepseek_api_key:
            print("❌ 错误：未配置API密钥")
            print("请在 config/default.yaml 或 config/dev.yaml 中配置API密钥")
            return
        
        # 2. 创建LLM服务
        print("🔧 正在初始化LLM服务...")
        service = LLMService(config)
        await service.initialize()
        print(f"✅ LLM服务初始化完成")
        print(f"   默认模型: {config.get('llm', {}).get('default_model', 'unknown')}")
        print(f"   已注册适配器: {list(service._adapters.keys())}")
        print()
        
        # 3. 准备问题
        question = "你好 你喜欢什么东西"
        messages = [{"role": "user", "content": question}]
        
        print("=" * 60)
        print(f"💬 问题: {question}")
        print("=" * 60)
        print()
        
        # 4. 如果配置了千问，使用千问回答
        if qwen_api_key:
            print("🤖 使用通义千问回答:")
            print("-" * 60)
            try:
                response = await service.chat(messages, model="qwen-turbo")
                print(response.content)
                print()
                print(f"📊 Token使用情况:")
                print(f"   - 提示Token: {response.usage.get('prompt_tokens', 0)}")
                print(f"   - 完成Token: {response.usage.get('completion_tokens', 0)}")
                print(f"   - 总Token: {response.total_tokens}")
                print()
            except Exception as e:
                print(f"❌ 调用失败: {e}")
                print()
        
        # 5. 如果配置了DeepSeek，使用DeepSeek回答
        if deepseek_api_key:
            print("🤖 使用DeepSeek回答:")
            print("-" * 60)
            try:
                response = await service.chat(messages, model="deepseek-chat")
                print(response.content)
                print()
                print(f"📊 Token使用情况:")
                print(f"   - 提示Token: {response.usage.get('prompt_tokens', 0)}")
                print(f"   - 完成Token: {response.usage.get('completion_tokens', 0)}")
                print(f"   - 总Token: {response.total_tokens}")
                print()
            except Exception as e:
                print(f"❌ 调用失败: {e}")
                print()
        
        # 6. 清理资源
        await service.cleanup()
        print("=" * 60)
        print("✅ 示例执行完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
