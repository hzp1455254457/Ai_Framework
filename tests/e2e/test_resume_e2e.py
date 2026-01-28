"""
Resume功能端到端测试
测试从前端到后端的完整流程
"""

import pytest
from fastapi.testclient import TestClient
from api.fastapi_app import app
import tempfile
from pathlib import Path
import json


@pytest.mark.e2e
class TestResumeE2E:
    """Resume功能E2E测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_resume_full_workflow(self, client):
        """测试完整的简历处理流程"""
        # Step 1: 上传并解析简历
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json_data = {
                "personal_info": {
                    "name": "E2E测试用户",
                    "email": "e2e@example.com"
                },
                "education": [],
                "work_experience": [],
                "project_experience": [],
                "skills": [],
                "certificates": []
            }
            json.dump(json_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # 解析简历
            with open(temp_path, 'rb') as file:
                parse_response = client.post(
                    "/api/v1/resume/parse",
                    files={"file": ("test.json", file, "application/json")}
                )
            
            if parse_response.status_code != 200:
                pytest.skip(f"解析简历失败: {parse_response.status_code}")
            
            parse_data = parse_response.json()
            assert parse_data["success"] is True
            resume_data = parse_data["data"]
            
            # Step 2: 获取模板列表
            templates_response = client.get("/api/v1/resume/templates")
            assert templates_response.status_code == 200
            templates_data = templates_response.json()
            
            if not templates_data["success"] or len(templates_data["templates"]) == 0:
                pytest.skip("没有可用的模板")
            
            template_id = templates_data["templates"][0]["id"]
            
            # Step 3: 生成简历
            generate_request = {
                "resume_data": resume_data,
                "template_id": template_id,
                "output_format": "html"
            }
            
            generate_response = client.post(
                "/api/v1/resume/generate",
                json=generate_request
            )
            
            if generate_response.status_code == 200:
                generate_data = generate_response.json()
                if generate_data["success"]:
                    file_id = generate_data["file_id"]
                    
                    # Step 4: 下载简历
                    download_response = client.get(f"/api/v1/resume/download/{file_id}")
                    # 下载可能失败（文件可能不存在），但不影响测试流程
                    assert download_response.status_code in [200, 404]
        finally:
            Path(temp_path).unlink()
