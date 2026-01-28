#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""详细测试简历功能"""
import asyncio
import httpx
import json
import sys
import traceback

async def test_optimize():
    """测试优化功能"""
    print("=" * 60)
    print("测试1: 优化简历功能")
    print("=" * 60)
    
    test_data = {
        "resume_data": {
            "personal_info": {
                "name": "测试用户",
                "email": "test@example.com"
            },
            "education": [],
            "work_experience": [],
            "project_experience": [],
            "skills": [{"category": "编程", "items": ["Python", "JavaScript"]}],
            "certificates": [],
            "languages": [],
            "awards": [],
            "publications": [],
            "volunteer_experience": []
        },
        "job_description": "软件工程师，熟悉Python开发",
        "optimization_level": "basic"  # 使用basic级别，减少token消耗
    }
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            print("\n发送优化请求...")
            print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)[:300]}")
            
            response = await client.post(
                "http://localhost:8000/api/v1/resume/optimize",
                json=test_data,
                timeout=180.0
            )
            
            print(f"\nHTTP状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✓ 优化成功！")
                    print(f"  优化耗时: {result.get('optimization_time', 0):.2f}秒")
                    if result.get("data"):
                        score = result["data"].get("score", 0)
                        print(f"  简历评分: {score}")
                        suggestions_count = len(result["data"].get("suggestions", []))
                        print(f"  优化建议数: {suggestions_count}")
                    return True
                else:
                    print(f"✗ 优化失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return False
                
    except httpx.ReadTimeout:
        print("✗ 请求超时（超过180秒）")
        return False
    except Exception as e:
        print(f"✗ 请求异常: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return False

async def test_generate():
    """测试生成功能"""
    print("\n" + "=" * 60)
    print("测试2: 生成简历功能")
    print("=" * 60)
    
    test_data = {
        "resume_data": {
            "personal_info": {
                "name": "测试用户",
                "email": "test@example.com"
            },
            "education": [],
            "work_experience": [],
            "project_experience": [],
            "skills": [{"category": "编程", "items": ["Python"]}],
            "certificates": [],
            "languages": [],
            "awards": [],
            "publications": [],
            "volunteer_experience": []
        },
        "template_id": "tech",
        "output_format": "html"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n发送生成请求...")
            response = await client.post(
                "http://localhost:8000/api/v1/resume/generate",
                json=test_data,
                timeout=30.0
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✓ 生成成功！")
                    file_id = result.get("file_id")
                    print(f"  文件ID: {file_id}")
                    
                    # 测试下载
                    download_url = result.get("download_url", "")
                    if download_url:
                        print(f"\n测试下载文件...")
                        download_response = await client.get(
                            f"http://localhost:8000{download_url}",
                            timeout=10.0
                        )
                        if download_response.status_code == 200:
                            print("✓ 文件下载成功")
                            content = download_response.text
                            if content.startswith("<!DOCTYPE html") or content.startswith("<html"):
                                print("✓ HTML文件格式正确")
                            return True
                        else:
                            print(f"✗ 文件下载失败: {download_response.status_code}")
                            return False
                    return True
                else:
                    print(f"✗ 生成失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"✗ 请求异常: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("\n开始详细测试简历功能...\n")
    
    # 先测试健康检查（重试3次）
    print("检查服务器状态...")
    for i in range(3):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                health = await client.get("http://localhost:8000/api/v1/health/")
                if health.status_code == 200:
                    print("✓ 服务器健康检查通过\n")
                    break
                else:
                    if i == 2:
                        print(f"✗ 服务器健康检查失败: {health.status_code}\n")
                        return 1
                    await asyncio.sleep(2)
        except Exception as e:
            if i == 2:
                print(f"✗ 无法连接到服务器: {e}\n")
                return 1
            await asyncio.sleep(2)
    
    # 测试优化
    optimize_ok = await test_optimize()
    
    # 测试生成
    generate_ok = await test_generate()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"优化简历: {'✓ 通过' if optimize_ok else '✗ 失败'}")
    print(f"生成简历: {'✓ 通过' if generate_ok else '✗ 失败'}")
    
    if optimize_ok and generate_ok:
        print("\n✓ 所有测试通过！功能已修复。")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查日志。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
