#!/usr/bin/env python3
"""测试工具注册"""

import asyncio
import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_tool_registration():
    """测试工具注册"""
    try:
        from core.agent.engine import AgentEngine
        from infrastructure.config.manager import ConfigManager
        
        print("=" * 60)
        print("测试工具注册")
        print("=" * 60)
        
        # 加载配置
        print("\n1. 加载配置...")
        cm = ConfigManager('config/default.yaml')
        await cm.initialize()
        config = cm.get_config()
        print("✅ 配置加载成功")
        
        # 检查配置
        print("\n2. 检查web_tools配置...")
        web_tools_config = config.get("agent", {}).get("web_tools", {})
        print(f"   web_tools.enabled: {web_tools_config.get('enabled', False)}")
        print(f"   web_search.enabled: {web_tools_config.get('web_search', {}).get('enabled', False)}")
        print(f"   fetch_webpage.enabled: {web_tools_config.get('fetch_webpage', {}).get('enabled', False)}")
        
        # 初始化Agent引擎
        print("\n3. 初始化Agent引擎...")
        engine = AgentEngine(config)
        await engine.initialize()
        print("✅ Agent引擎初始化完成")
        
        # 检查工具注册
        print("\n4. 检查工具注册...")
        tools = engine.get_tools()
        print(f"   已注册工具: {tools}")
        print(f"   工具数量: {len(tools)}")
        
        if len(tools) == 0:
            print("\n❌ 问题：没有注册任何工具！")
            print("   可能原因：")
            print("   1. web_tools.enabled = False")
            print("   2. 工具注册过程中出现异常")
            print("   3. 工具注册函数未正确调用")
        else:
            print(f"\n✅ 工具注册成功: {', '.join(tools)}")
        
        # 检查schema
        print("\n5. 检查工具schema...")
        schemas = engine.get_tool_schemas()
        print(f"   Schema数量: {len(schemas)}")
        
        if schemas:
            for i, schema in enumerate(schemas):
                func = schema.get("function", {})
                print(f"   Schema {i+1}: {func.get('name', 'N/A')}")
                print(f"      描述: {func.get('description', 'N/A')[:50]}...")
        else:
            print("   ⚠️  没有工具schema")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_registration())
