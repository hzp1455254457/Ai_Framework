"""
测试模块：加密服务测试
功能描述：测试EncryptionService和配置管理器加密集成
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from infrastructure.config.encryption import EncryptionService, EncryptionError
from infrastructure.config.manager import ConfigManager


@pytest.fixture
def master_key():
    """测试主密钥"""
    return "test-master-key-12345678901234567890"  # 至少32字符


@pytest.fixture
def encryption_service(master_key):
    """创建加密服务实例"""
    return EncryptionService(master_key=master_key)


@pytest.fixture
def encrypted_config(master_key):
    """创建带加密配置的配置字典"""
    service = EncryptionService(master_key=master_key)
    encrypted_api_key = service.encrypt("sk-test-api-key-12345")
    
    return {
        "llm": {
            "api_key": f"encrypted:{encrypted_api_key}",
            "timeout": 30
        },
        "encryption_key": master_key
    }


class TestEncryptionService:
    """EncryptionService测试类"""
    
    def test_encryption_service_initialization(self, master_key):
        """测试加密服务初始化"""
        service = EncryptionService(master_key=master_key)
        assert service is not None
    
    def test_encryption_service_without_key(self):
        """测试未提供主密钥时抛出异常"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EncryptionError, match="加密主密钥未配置"):
                EncryptionService()
    
    def test_encryption_service_short_key(self):
        """测试主密钥太短时抛出异常"""
        with pytest.raises(EncryptionError, match="主密钥长度至少需要16个字符"):
            EncryptionService(master_key="short")
    
    def test_encrypt_decrypt(self, encryption_service):
        """测试加密和解密"""
        plaintext = "sensitive-api-key-12345"
        
        # 加密
        encrypted = encryption_service.encrypt(plaintext)
        assert encrypted is not None
        assert encrypted != plaintext
        assert ":" in encrypted  # 加密格式应包含冒号分隔符
        
        # 解密
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_encrypt_empty_string(self, encryption_service):
        """测试加密空字符串"""
        encrypted = encryption_service.encrypt("")
        assert encrypted == ""
    
    def test_decrypt_empty_string(self, encryption_service):
        """测试解密空字符串"""
        decrypted = encryption_service.decrypt("")
        assert decrypted == ""
    
    def test_encrypt_decrypt_multiple_times(self, encryption_service):
        """测试多次加密同一明文产生不同密文（由于随机IV）"""
        plaintext = "same-plaintext"
        
        encrypted1 = encryption_service.encrypt(plaintext)
        encrypted2 = encryption_service.encrypt(plaintext)
        
        # 密文应该不同（因为IV是随机的）
        assert encrypted1 != encrypted2
        
        # 但解密后应该相同
        assert encryption_service.decrypt(encrypted1) == plaintext
        assert encryption_service.decrypt(encrypted2) == plaintext
    
    def test_decrypt_invalid_format(self, encryption_service):
        """测试解密无效格式"""
        with pytest.raises(EncryptionError, match="加密字符串格式错误"):
            encryption_service.decrypt("invalid-format")
    
    def test_decrypt_wrong_key(self, master_key):
        """测试使用错误密钥解密"""
        service1 = EncryptionService(master_key=master_key)
        service2 = EncryptionService(master_key="different-key-12345678901234567890")
        
        plaintext = "sensitive-data"
        encrypted = service1.encrypt(plaintext)
        
        # 使用错误密钥解密应该失败
        with pytest.raises(EncryptionError, match="解密失败"):
            service2.decrypt(encrypted)
    
    def test_is_encrypted(self, encryption_service):
        """测试检查加密格式"""
        plaintext = "sensitive-data"
        encrypted = encryption_service.encrypt(plaintext)
        
        assert encryption_service.is_encrypted(encrypted) is True
        assert encryption_service.is_encrypted(plaintext) is False
        assert encryption_service.is_encrypted("") is False
        assert encryption_service.is_encrypted("invalid:format") is False


class TestConfigManagerEncryption:
    """ConfigManager加密集成测试类"""
    
    def test_get_encrypted_config(self, encrypted_config):
        """测试获取加密配置"""
        config = ConfigManager(encrypted_config)
        
        # 获取加密的API密钥，应该自动解密
        api_key = config.get("llm.api_key")
        assert api_key == "sk-test-api-key-12345"
        assert api_key != encrypted_config["llm"]["api_key"]
    
    def test_get_plain_config(self, master_key):
        """测试获取明文配置（向后兼容）"""
        plain_config = {
            "llm": {
                "api_key": "sk-plain-api-key",
                "timeout": 30
            }
        }
        config = ConfigManager(plain_config)
        
        # 明文配置应该正常返回
        api_key = config.get("llm.api_key")
        assert api_key == "sk-plain-api-key"
    
    def test_set_encrypted_config(self, master_key):
        """测试设置加密配置"""
        config = ConfigManager({
            "encryption_key": master_key
        })
        
        # 设置加密配置
        config.set("llm.api_key", "sk-secret-key", encrypt=True)
        
        # 获取时应该自动解密
        api_key = config.get("llm.api_key")
        assert api_key == "sk-secret-key"
        
        # 原始配置应该是加密格式
        raw_value = config._config["llm"]["api_key"]
        assert raw_value.startswith("encrypted:")
    
    def test_set_plain_config(self):
        """测试设置明文配置"""
        config = ConfigManager({})
        
        # 设置明文配置
        config.set("llm.api_key", "sk-plain-key", encrypt=False)
        
        # 获取时应该返回明文
        api_key = config.get("llm.api_key")
        assert api_key == "sk-plain-key"
        assert not api_key.startswith("encrypted:")
    
    def test_encrypt_value(self, master_key):
        """测试encrypt_value方法"""
        config = ConfigManager({
            "encryption_key": master_key
        })
        
        plaintext = "sensitive-data"
        encrypted = config.encrypt_value(plaintext)
        
        assert encrypted.startswith("encrypted:")
        assert config.decrypt_value(encrypted) == plaintext
    
    def test_decrypt_value(self, master_key):
        """测试decrypt_value方法"""
        service = EncryptionService(master_key=master_key)
        encrypted = service.encrypt("sensitive-data")
        
        config = ConfigManager({
            "encryption_key": master_key
        })
        
        decrypted = config.decrypt_value(f"encrypted:{encrypted}")
        assert decrypted == "sensitive-data"
    
    def test_encrypt_value_without_service(self):
        """测试未初始化加密服务时调用encrypt_value"""
        config = ConfigManager({})
        
        with pytest.raises(EncryptionError, match="加密服务未初始化"):
            config.encrypt_value("sensitive-data")
    
    def test_decrypt_value_without_service(self):
        """测试未初始化加密服务时调用decrypt_value"""
        config = ConfigManager({})
        
        with pytest.raises(EncryptionError, match="加密服务未初始化"):
            config.decrypt_value("encrypted:test")
    
    def test_set_encrypt_without_service(self):
        """测试未初始化加密服务时设置加密配置"""
        config = ConfigManager({})
        
        with pytest.raises(EncryptionError, match="加密服务未初始化"):
            config.set("llm.api_key", "sk-key", encrypt=True)
    
    def test_get_encrypted_without_service(self):
        """测试未初始化加密服务时获取加密配置（向后兼容）"""
        # 配置中有加密值，但没有加密服务
        config = ConfigManager({
            "llm": {
                "api_key": "encrypted:test:encrypted:value"
            }
        })
        
        # 应该返回原始值（向后兼容）
        api_key = config.get("llm.api_key")
        assert api_key == "encrypted:test:encrypted:value"
    
    def test_config_loader_preserves_encrypted_format(self, master_key):
        """测试配置加载器保持加密格式"""
        from infrastructure.config.loader import ConfigLoader
        
        # 创建临时配置文件
        import tempfile
        import yaml
        
        encrypted_service = EncryptionService(master_key=master_key)
        encrypted_value = encrypted_service.encrypt("test-api-key")
        
        config_data = {
            "llm": {
                "api_key": f"encrypted:{encrypted_value}"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader()
            loaded_config = loader.load_yaml(temp_path)
            
            # 加载的配置应该保持加密格式
            assert loaded_config["llm"]["api_key"].startswith("encrypted:")
        finally:
            import os
            os.unlink(temp_path)
    
    def test_config_validator_encrypted_format(self, master_key):
        """测试配置验证器验证加密格式"""
        from infrastructure.config.validator import ConfigValidator
        
        validator = ConfigValidator()
        
        # 有效加密格式
        valid_config = {
            "llm": {
                "api_key": "encrypted:salt:iv:ciphertext:tag"
            }
        }
        assert validator.validate(valid_config) is True
        
        # 无效加密格式
        invalid_config = {
            "llm": {
                "api_key": "encrypted:invalid-format"
            }
        }
        with pytest.raises(Exception):  # ConfigValidationError
            validator.validate(invalid_config)
