#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试简历优化和导出功能
"""

import asyncio
import json
import httpx
from pathlib import Path

async def test_optimize_resume():
    """测试优化简历功能"""
    print("=" * 60)
    print("测试1: 优化简历功能")
    print("=" * 60)
    
    # 准备测试数据
    test_resume = {
        "personal_info": {
            "name": "测试用户",
            "email": "test@example.com",
            "phone": "13800138000"
        },
        "education": [],
        "work_experience": [],
        "project_experience": [],
        "skills": [
            {
                "category": "编程语言",
                "items": ["Python", "JavaScript", "TypeScript"]
            }
        ],
        "certificates": [],
        "languages": [],
        "awards": [],
        "publications": [],
        "volunteer_experience": []
    }
    
    request_data = {
        "resume_data": test_resume,
        "job_description": "软件工程师，熟悉Python和Web开发",
        "optimization_level": "basic"
    }
    
    try:
        async with httpx.AsyncClient(timeout=200.0) as client:
            print(f"\n发送优化请求...")
            response = await client.post(
                "http://localhost:8000/api/v1/resume/optimize",
                json=request_data,
                timeout=200.0
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
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
                print(f"  响应: {response.text[:200]}")
                return False
    except httpx.ReadTimeout:
        print("✗ 请求超时（超过200秒）")
        return False
    except Exception as e:
        print(f"✗ 请求失败: {type(e).__name__}: {str(e)}")
        return False

async def test_generate_resume():
    """测试生成简历功能"""
    print("\n" + "=" * 60)
    print("测试2: 生成简历功能")
    print("=" * 60)
    
    # 使用之前解析的简历数据或创建测试数据
    test_resume = {
        "personal_info": {
            "name": "测试用户",
            "email": "test@example.com",
            "phone": "13800138000"
        },
        "education": [],
        "work_experience": [],
        "project_experience": [],
        "skills": [
            {
                "category": "编程语言",
                "items": ["Python", "JavaScript"]
            }
        ],
        "certificates": [],
        "languages": [],
        "awards": [],
        "publications": [],
        "volunteer_experience": []
    }
    
    request_data = {
        "resume_data": test_resume,
        "template_id": "tech",
        "output_format": "html"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n发送生成请求...")
            response = await client.post(
                "http://localhost:8000/api/v1/resume/generate",
                json=request_data,
                timeout=30.0
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✓ 生成成功！")
                    file_id = result.get("file_id")
                    print(f"  文件ID: {file_id}")
                    print(f"  生成耗时: {result.get('generation_time', 0):.2f}秒")
                    
                    # 测试下载
                    download_url = result.get("download_url", "")
                    if download_url:
                        print(f"\n测试下载文件: {download_url}")
                        download_response = await client.get(
                            f"http://localhost:8000{download_url}",
                            timeout=10.0
                        )
                        if download_response.status_code == 200:
                            print("✓ 文件下载成功")
                            # 检查文件内容
                            content = download_response.text
                            if content.startswith("<!DOCTYPE html"):
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
                print(f"  响应: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"✗ 请求失败: {type(e).__name__}: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("\n开始测试简历功能...\n")
    
    # 测试优化
    optimize_ok = await test_optimize_resume()
    
    # 测试生成
    generate_ok = await test_generate_resume()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"优化简历: {'✓ 通过' if optimize_ok else '✗ 失败'}")
    print(f"生成简历: {'✓ 通过' if generate_ok else '✗ 失败'}")
    
    if optimize_ok and generate_ok:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查日志")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
