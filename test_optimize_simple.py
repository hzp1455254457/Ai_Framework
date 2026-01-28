#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import httpx
import json

async def test():
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
            print("发送优化请求...")
            response = await client.post(
                "http://localhost:8000/api/v1/resume/optimize",
                json=test_data,
                timeout=180.0
            )
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n成功! {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
            else:
                print(f"\n失败: {response.text}")
    except Exception as e:
        print(f"异常: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
