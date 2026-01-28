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
        "template_id": "tech",
        "output_format": "html"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("发送生成请求...")
            response = await client.post(
                "http://localhost:8000/api/v1/resume/generate",
                json=test_data,
                timeout=30.0
            )
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n成功! {json.dumps(result, ensure_ascii=False, indent=2)[:300]}")
                return True
            else:
                print(f"\n失败: {response.text}")
                return False
    except Exception as e:
        print(f"异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)
