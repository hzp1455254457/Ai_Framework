
import pytest
import httpx
import base64

@pytest.mark.asyncio
async def test_image_edit_base64_validation():
    url = "http://localhost:8000/api/v1/vision/edit"
    
    # Create a fake base64 image
    fake_base64 = "data:image/png;base64," + "a" * 1000
    
    payload = {
        "image": fake_base64,
        "prompt": "变成赛博朋克风格",
        "n": 1,
        "size": "1024x1024",
        "adapter_name": "tongyi-wanxiang-adapter"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Expect 503 (Service Unavailable) or 500 because adapter error usually maps to 503 or 500 in routes
        # In api/routes/vision.py, VisionAdapterError might be caught.
        
        assert "通义万相API仅支持公开可访问的图像URL" in response.text or "无效的图像URL" in response.text

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_image_edit_base64_validation())
