"""
测试互联网访问工具
"""
import asyncio
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.agent.tools.web_tools import web_search, fetch_webpage
from core.agent.tools.tools import ToolError


async def test_web_search():
    """测试web_search工具"""
    print("=" * 60)
    print("测试 web_search 工具")
    print("=" * 60)
    
    try:
        result = await web_search(
            query="Python async programming",
            max_results=3,
            search_engine="duckduckgo",
            timeout=15.0,
            max_retries=2
        )
        print("✓ web_search 执行成功")
        print(f"\n结果预览（前500字符）：\n{result[:500]}...")
        return True
    except ToolError as e:
        print(f"✗ web_search 执行失败: {e}")
        return False
    except Exception as e:
        print(f"✗ web_search 发生异常: {type(e).__name__}: {e}")
        return False


async def test_fetch_webpage():
    """测试fetch_webpage工具"""
    print("\n" + "=" * 60)
    print("测试 fetch_webpage 工具")
    print("=" * 60)
    
    try:
        result = await fetch_webpage(
            url="https://www.python.org",
            timeout=15.0,
            max_retries=2,
            max_length=1000
        )
        print("✓ fetch_webpage 执行成功")
        print(f"\n结果预览（前500字符）：\n{result[:500]}...")
        return True
    except ToolError as e:
        print(f"✗ fetch_webpage 执行失败: {e}")
        return False
    except Exception as e:
        print(f"✗ fetch_webpage 发生异常: {type(e).__name__}: {e}")
        return False


async def test_agent_tools_registration():
    """测试Agent工具注册"""
    print("\n" + "=" * 60)
    print("测试 Agent 工具注册")
    print("=" * 60)
    
    try:
        from infrastructure.config.manager import ConfigManager
        from core.agent.engine import AgentEngine
        
        # 加载配置
        config_manager = ConfigManager.load()
        config = config_manager.config
        
        # 创建Agent引擎
        engine = AgentEngine(config)
        await engine.initialize()
        
        # 获取工具列表
        tools = engine.get_tools()
        tool_schemas = engine.get_tool_schemas()
        
        print(f"✓ Agent引擎初始化成功")
        print(f"✓ 已注册工具数量: {len(tools)}")
        print(f"\n工具列表:")
        for tool_name in tools:
            print(f"  - {tool_name}")
        
        # 检查互联网工具是否注册
        web_tools = ["web_search", "fetch_webpage"]
        found_tools = [tool for tool in web_tools if tool in tools]
        
        if found_tools:
            print(f"\n✓ 互联网工具已注册: {', '.join(found_tools)}")
            
            # 显示工具schema
            for schema in tool_schemas:
                if schema["name"] in web_tools:
                    print(f"\n工具 {schema['name']} 的schema:")
                    print(json.dumps(schema, indent=2, ensure_ascii=False))
        else:
            print(f"\n✗ 互联网工具未注册")
            print(f"  期望的工具: {', '.join(web_tools)}")
            print(f"  实际工具: {', '.join(tools)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Agent工具注册测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("互联网访问工具测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: web_search
    results.append(await test_web_search())
    
    # 测试2: fetch_webpage
    results.append(await test_fetch_webpage())
    
    # 测试3: Agent工具注册
    results.append(await test_agent_tools_registration())
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {len(results)}")
    print(f"成功: {sum(results)}")
    print(f"失败: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
