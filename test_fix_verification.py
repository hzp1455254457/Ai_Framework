#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证修复后的功能"""
import asyncio
import httpx
import json

async def test_optimize():
    """测试优化功能"""
    print("=" * 60)
    print("测试优化简历功能")
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
        "job_description": "软件工程师",
        "optimization_level": "basic"
    }
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            print("\n发送优化请求...")
            response = await client.post(
                "http://localhost:8000/api/v1/resume/optimize",
                json=test_data,
                timeout=180.0
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✓ 优化成功！")
                    data = result.get("data")
                    if data:
                        score = data.get("score")
                        suggestions_count = len(data.get("suggestions", []))
                        optimized_resume = data.get("optimized_resume")
                        
                        print(f"  评分: {score}")
                        print(f"  建议数: {suggestions_count}")
                        
                        if optimized_resume and optimized_resume.get("personal_info"):
                            name = optimized_resume["personal_info"].get("name")
                            print(f"  优化后姓名: {name}")
                            if name and name != "测试用户":
                                print("  ✓ 优化后的简历数据正确")
                            else:
                                print("  ⚠ 优化后的简历数据可能未更新")
                        
                        return True
                    else:
                        print("  ✗ 优化结果数据为空")
                        return False
                else:
                    print(f"✗ 优化失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                print(f"响应: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"✗ 请求异常: {type(e).__name__}: {str(e)}")
        return False

async def test_generate():
    """测试生成功能"""
    print("\n" + "=" * 60)
    print("测试生成简历功能")
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
                            content = download_response.text
                            print(f"  文件大小: {len(content)} 字节")
                            
                            # 检查内容
                            if "测试用户" in content:
                                print("  ✓ HTML包含姓名，渲染正常")
                            else:
                                print("  ✗ HTML未包含姓名")
                                print(f"  内容预览: {content[:200]}")
                            
                            if "test@example.com" in content:
                                print("  ✓ HTML包含邮箱，渲染正常")
                            else:
                                print("  ✗ HTML未包含邮箱")
                            
                            return True
                        else:
                            print(f"  ✗ 文件下载失败: {download_response.status_code}")
                            return False
                    return True
                else:
                    print(f"✗ 生成失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                print(f"响应: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"✗ 请求异常: {type(e).__name__}: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("\n开始验证修复后的功能...\n")
    
    optimize_ok = await test_optimize()
    generate_ok = await test_generate()
    
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    print(f"优化简历: {'✓ 通过' if optimize_ok else '✗ 失败'}")
    print(f"生成简历: {'✓ 通过' if generate_ok else '✗ 失败'}")
    
    if optimize_ok and generate_ok:
        print("\n✓ 所有功能修复完成！")
        return 0
    else:
        print("\n✗ 部分功能仍需修复")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
