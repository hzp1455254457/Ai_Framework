import httpx
import json
import sys
import asyncio

async def test_image_edit():
    url = "http://localhost:8000/api/v1/vision/edit"
    
    # 使用一个公开的可访问图像 (使用DashScope官方示例图片)
    image_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg" 
    
    payload = {
        "image": image_url,
        "prompt": "变成赛博朋克风格",
        "n": 1,
        "size": "1024x1024",
        "adapter_name": "tongyi-wanxiang-adapter"
    }
    
    print(f"Sending request to {url}...")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("Response:")
                print(json.dumps(response.json(), ensure_ascii=False, indent=2))
            else:
                print("Error Response:")
                print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_image_edit())
