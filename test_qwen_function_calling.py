#!/usr/bin/env python3
"""
测试通义千问是否支持Function Calling（工具调用）

此脚本用于验证通义千问API是否支持tools参数和工具调用功能。
"""

import asyncio
import json
from typing import Dict, Any, Optional
from httpx import AsyncClient, HTTPError


class QwenFunctionCallingTester:
    """通义千问Function Calling测试器"""
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/api/v1"):
        """
        初始化测试器
        
        参数:
            api_key: 通义千问API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client: Optional[AsyncClient] = None
    
    async def initialize(self):
        """初始化HTTP客户端"""
        self.client = AsyncClient(
            base_url=self.base_url,
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
    
    def create_web_search_tool(self) -> Dict[str, Any]:
        """创建web_search工具定义"""
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "通过搜索引擎查询互联网内容，返回搜索结果摘要",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询关键词"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大返回结果数",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    async def test_without_tools(self, model: str = "qwen-turbo") -> Dict[str, Any]:
        """测试1：不使用工具的正常调用"""
        print("\n" + "="*60)
        print("测试1：不使用工具的正常调用")
        print("="*60)
        
        request_data = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "user", "content": "请告诉我Python异步编程的基本概念"}
                ]
            },
            "parameters": {
                "temperature": 0.7,
            }
        }
        
        try:
            response = await self.client.post(
                "/services/aigc/text-generation/generation",
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()
            
            print("✅ 请求成功")
            print(f"响应状态码: {response.status_code}")
            
            # 解析响应
            output = result.get("output", {})
            if "choices" in output:
                content = output["choices"][0].get("message", {}).get("content", "")
                print(f"响应内容长度: {len(content)} 字符")
                print(f"响应内容（前200字符）: {content[:200]}...")
            
            return {"success": True, "result": result}
            
        except HTTPError as e:
            print(f"❌ 请求失败: HTTP {e.response.status_code}")
            print(f"错误信息: {e.response.text}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_with_tools_in_input(self, model: str = "qwen-turbo") -> Dict[str, Any]:
        """测试2：在input中传递tools参数"""
        print("\n" + "="*60)
        print("测试2：在input中传递tools参数")
        print("="*60)
        
        tool = self.create_web_search_tool()
        
        request_data = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "user", "content": "请使用web_search工具搜索Python异步编程的最新信息"}
                ],
                "tools": [tool]  # 在input中传递tools
            },
            "parameters": {
                "temperature": 0.7,
            }
        }
        
        print(f"请求数据（tools）: {json.dumps(tool, ensure_ascii=False, indent=2)}")
        
        try:
            response = await self.client.post(
                "/services/aigc/text-generation/generation",
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()
            
            print("✅ 请求成功")
            print(f"响应状态码: {response.status_code}")
            
            # 检查响应中是否包含工具调用
            output = result.get("output", {})
            if "choices" in output:
                choice = output["choices"][0]
                message = choice.get("message", {})
                content = message.get("content", "")
                
                print(f"响应内容长度: {len(content)} 字符")
                print(f"响应内容（前200字符）: {content[:200]}...")
                
                # 检查工具调用
                tool_calls = message.get("tool_calls")
                function_call = message.get("function_call")
                
                if tool_calls:
                    print(f"\n✅ 检测到tool_calls: {len(tool_calls)} 个")
                    for i, tc in enumerate(tool_calls):
                        print(f"   工具调用 {i+1}:")
                        print(f"     函数: {tc.get('function', {}).get('name', 'N/A')}")
                        print(f"     参数: {tc.get('function', {}).get('arguments', 'N/A')}")
                elif function_call:
                    print(f"\n✅ 检测到function_call:")
                    print(f"   函数: {function_call.get('name', 'N/A')}")
                    print(f"   参数: {function_call.get('arguments', 'N/A')}")
                else:
                    print("\n⚠️  未检测到工具调用")
                    print("   可能原因:")
                    print("   1. 模型不支持Function Calling")
                    print("   2. tools参数格式不正确")
                    print("   3. 模型没有选择使用工具")
            
            return {"success": True, "result": result, "has_tool_calls": bool(tool_calls or function_call)}
            
        except HTTPError as e:
            print(f"❌ 请求失败: HTTP {e.response.status_code}")
            error_text = e.response.text
            print(f"错误信息: {error_text}")
            
            # 检查是否是参数格式错误
            if "tools" in error_text.lower() or "invalid" in error_text.lower():
                print("\n⚠️  可能是tools参数格式不被支持")
            
            return {"success": False, "error": str(e), "error_text": error_text}
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_with_tools_in_parameters(self, model: str = "qwen-turbo") -> Dict[str, Any]:
        """测试3：在parameters中传递tools参数"""
        print("\n" + "="*60)
        print("测试3：在parameters中传递tools参数")
        print("="*60)
        
        tool = self.create_web_search_tool()
        
        request_data = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "user", "content": "请使用web_search工具搜索Python异步编程的最新信息"}
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "tools": [tool]  # 在parameters中传递tools
            }
        }
        
        print(f"请求数据（tools）: {json.dumps(tool, ensure_ascii=False, indent=2)}")
        
        try:
            response = await self.client.post(
                "/services/aigc/text-generation/generation",
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()
            
            print("✅ 请求成功")
            print(f"响应状态码: {response.status_code}")
            
            # 检查响应中是否包含工具调用
            output = result.get("output", {})
            if "choices" in output:
                choice = output["choices"][0]
                message = choice.get("message", {})
                content = message.get("content", "")
                
                print(f"响应内容长度: {len(content)} 字符")
                print(f"响应内容（前200字符）: {content[:200]}...")
                
                # 检查工具调用
                tool_calls = message.get("tool_calls")
                function_call = message.get("function_call")
                
                if tool_calls:
                    print(f"\n✅ 检测到tool_calls: {len(tool_calls)} 个")
                    for i, tc in enumerate(tool_calls):
                        print(f"   工具调用 {i+1}:")
                        print(f"     函数: {tc.get('function', {}).get('name', 'N/A')}")
                        print(f"     参数: {tc.get('function', {}).get('arguments', 'N/A')}")
                elif function_call:
                    print(f"\n✅ 检测到function_call:")
                    print(f"   函数: {function_call.get('name', 'N/A')}")
                    print(f"   参数: {function_call.get('arguments', 'N/A')}")
                else:
                    print("\n⚠️  未检测到工具调用")
            
            return {"success": True, "result": result, "has_tool_calls": bool(tool_calls or function_call)}
            
        except HTTPError as e:
            print(f"❌ 请求失败: HTTP {e.response.status_code}")
            error_text = e.response.text
            print(f"错误信息: {error_text}")
            
            if "tools" in error_text.lower() or "invalid" in error_text.lower():
                print("\n⚠️  可能是tools参数格式不被支持")
            
            return {"success": False, "error": str(e), "error_text": error_text}
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_different_models(self) -> Dict[str, Any]:
        """测试4：测试不同模型是否支持Function Calling"""
        print("\n" + "="*60)
        print("测试4：测试不同模型是否支持Function Calling")
        print("="*60)
        
        models = ["qwen-turbo", "qwen-plus", "qwen-max"]
        results = {}
        
        for model in models:
            print(f"\n--- 测试模型: {model} ---")
            result = await self.test_with_tools_in_input(model=model)
            results[model] = result
            await asyncio.sleep(1)  # 避免请求过快
        
        return results
    
    async def run_all_tests(self, model: str = "qwen-turbo"):
        """运行所有测试"""
        print("\n" + "="*60)
        print("通义千问 Function Calling 支持测试")
        print("="*60)
        print(f"测试模型: {model}")
        print(f"API端点: {self.base_url}")
        
        results = {}
        
        # 测试1：不使用工具
        results["test1_normal"] = await self.test_without_tools(model)
        await asyncio.sleep(1)
        
        # 测试2：在input中传递tools
        results["test2_tools_in_input"] = await self.test_with_tools_in_input(model)
        await asyncio.sleep(1)
        
        # 测试3：在parameters中传递tools
        results["test3_tools_in_parameters"] = await self.test_with_tools_in_parameters(model)
        
        # 生成测试报告
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results: Dict[str, Any]):
        """生成测试报告"""
        print("\n" + "="*60)
        print("测试报告")
        print("="*60)
        
        # 检查是否有成功的工具调用
        has_function_calling = False
        for key, result in results.items():
            if result.get("success") and result.get("has_tool_calls"):
                has_function_calling = True
                print(f"\n✅ {key}: 支持Function Calling")
            elif result.get("success"):
                print(f"\n⚠️  {key}: 请求成功但未检测到工具调用")
            else:
                print(f"\n❌ {key}: 请求失败")
                if "error_text" in result:
                    print(f"   错误: {result['error_text'][:200]}")
        
        print("\n" + "="*60)
        if has_function_calling:
            print("结论: ✅ 通义千问支持Function Calling")
            print("建议: 可以在Agent模式中使用工具调用功能")
        else:
            print("结论: ❌ 通义千问可能不支持Function Calling")
            print("建议: 考虑切换到支持Function Calling的模型（如OpenAI GPT）")
        print("="*60)


async def main():
    """主函数"""
    import sys
    
    # 从配置文件读取API密钥
    try:
        import yaml
        with open("config/default.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        api_key = config.get("llm", {}).get("adapters", {}).get("qwen-adapter", {}).get("api_key", "")
    except Exception as e:
        print(f"⚠️  无法从配置文件读取API密钥: {e}")
        api_key = ""
    
    # 如果配置文件中没有，从命令行参数或环境变量获取
    if not api_key:
        if len(sys.argv) > 1:
            api_key = sys.argv[1]
        else:
            import os
            api_key = os.getenv("QWEN_API_KEY", "")
    
    if not api_key:
        print("❌ 错误: 未提供通义千问API密钥")
        print("\n使用方法:")
        print("  1. 在config/default.yaml中配置qwen-adapter.api_key")
        print("  2. 或通过命令行参数: python test_qwen_function_calling.py <api_key>")
        print("  3. 或通过环境变量: set QWEN_API_KEY=<api_key>")
        return
    
    # 创建测试器
    tester = QwenFunctionCallingTester(api_key=api_key)
    
    try:
        await tester.initialize()
        
        # 运行所有测试
        await tester.run_all_tests(model="qwen-turbo")
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
