"""简单测试脚本"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

async def test():
    try:
        from core.agent.tools.web_tools import web_search
        print("开始测试 web_search...")
        result = await web_search("Python", max_results=2, timeout=15.0)
        print(f"成功！结果长度: {len(result)}")
        print(f"前300字符: {result[:300]}")
        return True
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
