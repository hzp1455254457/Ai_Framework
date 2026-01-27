import pytest
import base64
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from core.vision.adapters.tongyi_wanxiang_adapter import TongYiWanXiangAdapter
from core.vision.models import ImageEditRequest, ImageEditResponse
from core.vision.adapters.base import VisionAdapterError

@pytest.fixture
def adapter():
    adapter = TongYiWanXiangAdapter({"api_key": "test_key"})
    adapter._initialized = True
    return adapter

@pytest.fixture
def mock_upload():
    # Patch DashScopeFile in the adapter module
    with patch('core.vision.adapters.tongyi_wanxiang_adapter.DashScopeFile') as mock_file_cls:
        # Configure successful upload response
        mock_file_cls.upload.return_value.output.url = "http://oss/image.png"
        
        # Also patch dashscope module variable in the adapter to ensure it's not None
        with patch('core.vision.adapters.tongyi_wanxiang_adapter.dashscope'):
            yield mock_file_cls

@pytest.mark.asyncio
async def test_upload_image_success(adapter, mock_upload):
    """测试Base64图片上传成功"""
    base64_str = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    url = adapter._upload_image_to_dashscope(base64_str)
    
    assert url == "http://oss/image.png"
    mock_upload.upload.assert_called_once()
    
    # 验证是否正确解码并写入临时文件
    args, kwargs = mock_upload.upload.call_args
    # First argument is file path
    assert args[0].endswith(".png")
    # Verify purpose is set to inference
    assert kwargs.get('purpose') == 'inference'
    # Verify model is set
    assert kwargs.get('model') == 'wanx-v1'

@pytest.mark.asyncio
async def test_upload_image_invalid_base64(adapter, mock_upload):
    """测试无效Base64数据"""
    with pytest.raises(VisionAdapterError, match="无效的Base64数据"):
        adapter._upload_image_to_dashscope("invalid_base64")

@pytest.mark.asyncio
async def test_upload_image_no_url(adapter, mock_upload):
    """测试上传未返回URL"""
    # Mock return value to not have output.url
    # Case 1: Result has output but no url (or empty url)
    mock_result = MagicMock()
    # Need to make sure getattr(mock_result.output, 'url') raises AttributeError or returns None
    # MagicMock by default creates new mocks for attributes
    # So we need to explicitly set them to None or configure spec
    
    # Approach: return an object that has output but no url attribute
    class Result:
        class Output:
            pass
        output = Output()
        
    mock_upload.upload.return_value = Result()
    
    with pytest.raises(VisionAdapterError, match="上传图片到DashScope失败"):
        adapter._upload_image_to_dashscope("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")

@pytest.mark.asyncio
async def test_edit_image_with_base64(adapter):
    """测试使用Base64调用edit_image"""
    # Mock _client
    adapter._client = AsyncMock()
    
    # Mock response object
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"task_id": "task_123"}
    }
    adapter._client.post.return_value = mock_response
    
    mock_task_response = MagicMock()
    mock_task_response.json.return_value = {
        "output": {"task_status": "SUCCEEDED", "results": [{"url": "http://result.png"}]}
    }
    adapter._client.get.return_value = mock_task_response
    
    # Mock upload method directly to avoid file ops
    with patch.object(adapter, '_upload_image_to_dashscope', return_value="http://oss/uploaded.png") as mock_upload_method:
        
        request = ImageEditRequest(
            prompt="change color",
            image="data:image/png;base64,fake",
            mask="data:image/png;base64,fake_mask"
        )
        
        response = await adapter.edit_image(request)
        
        assert isinstance(response, ImageEditResponse)
        assert mock_upload_method.call_count == 2 # Image + Mask
        
        # Verify API call used URLs
        call_args = adapter._client.post.call_args
        json_body = call_args.kwargs['json']
        assert json_body['input']['base_image_url'] == "http://oss/uploaded.png"
        assert json_body['input']['mask_image_url'] == "http://oss/uploaded.png"

@pytest.mark.asyncio
async def test_edit_image_with_url_skips_upload(adapter):
    """测试使用URL调用edit_image跳过上传"""
    adapter._client = AsyncMock()
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "output": {"task_id": "task_123"}
    }
    adapter._client.post.return_value = mock_response
    
    mock_task_response = MagicMock()
    mock_task_response.json.return_value = {
        "output": {"task_status": "SUCCEEDED", "results": [{"url": "http://result.png"}]}
    }
    adapter._client.get.return_value = mock_task_response
    
    with patch.object(adapter, '_upload_image_to_dashscope') as mock_upload_method:
        
        request = ImageEditRequest(
            prompt="change color",
            image="http://example.com/image.png"
        )
        
        await adapter.edit_image(request)
        
        mock_upload_method.assert_not_called()

@pytest.mark.asyncio
async def test_upload_image_uploaded_file_url(adapter, mock_upload):
    """测试返回 uploaded_file_url 字段的情况"""
    base64_str = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    # Configure mock to return uploaded_file_url
    # Use a real class to avoid MagicMock auto-creation
    class Output:
        uploaded_file_url = "http://oss/uploaded_file.png"
    
    class Result:
        output = Output()
        
    mock_upload.upload.return_value = Result()
    
    url = adapter._upload_image_to_dashscope(base64_str)
    
    assert url == "http://oss/uploaded_file.png"

@pytest.mark.asyncio
async def test_upload_image_dict_response(adapter, mock_upload):
    """测试返回字典格式响应的情况"""
    base64_str = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    # Configure mock to return dict
    mock_upload.upload.return_value = {
        "output": {
            "uploaded_file_url": "http://oss/dict_url.png"
        }
    }
    
    url = adapter._upload_image_to_dashscope(base64_str)
    
    assert url == "http://oss/dict_url.png"
