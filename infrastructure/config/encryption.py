"""
模块名称：加密服务模块
功能描述：提供配置加密/解密功能，支持API密钥等敏感信息的加密存储
创建日期：2026-01-23
最后更新：2026-01-23
维护者：AI框架团队

主要类：
    - EncryptionService: 加密服务类
    - EncryptionError: 加密错误异常

依赖模块：
    - cryptography: Python加密库
    - os: 环境变量访问
    - base64: Base64编码
"""

import os
import base64
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class EncryptionError(Exception):
    """加密错误异常"""
    pass


class EncryptionService:
    """
    加密服务
    
    提供配置加密/解密功能，支持API密钥等敏感信息的加密存储。
    
    特性：
        - 使用 AES-256-GCM 对称加密
        - 使用 PBKDF2 密钥派生
        - 支持主密钥从环境变量或配置文件读取
        - 自动生成随机IV（初始化向量）
    
    配置示例:
        {
            "encryption_key": "your-master-key-here"  # 或通过环境变量 ENCRYPTION_KEY
        }
    
    示例:
        >>> service = EncryptionService()
        >>> encrypted = service.encrypt("sensitive-data")
        >>> decrypted = service.decrypt(encrypted)
    """
    
    # 加密算法常量
    ALGORITHM = "AES-256-GCM"
    KEY_SIZE = 32  # 256 bits
    IV_SIZE = 12  # 96 bits for GCM
    SALT_SIZE = 16  # 128 bits
    PBKDF2_ITERATIONS = 100000  # PBKDF2迭代次数
    
    def __init__(self, master_key: Optional[str] = None) -> None:
        """
        初始化加密服务
        
        参数:
            master_key: 主密钥（可选，如果未提供则从环境变量读取）
        
        异常:
            EncryptionError: 主密钥未配置时抛出
        """
        self._master_key: Optional[str] = master_key or os.getenv("ENCRYPTION_KEY")
        
        if not self._master_key:
            raise EncryptionError(
                "加密主密钥未配置。请设置环境变量 ENCRYPTION_KEY 或在配置中提供 encryption_key"
            )
        
        if len(self._master_key) < 16:
            raise EncryptionError("主密钥长度至少需要16个字符")
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        从主密钥派生加密密钥
        
        使用 PBKDF2 从主密钥派生固定长度的加密密钥。
        
        参数:
            salt: 盐值（随机生成）
        
        返回:
            派生后的加密密钥（32字节）
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(self._master_key.encode("utf-8"))
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文数据
        
        使用 AES-256-GCM 加密数据，返回Base64编码的加密字符串。
        格式：salt:iv:encrypted_data:tag
        
        参数:
            plaintext: 要加密的明文数据
        
        返回:
            Base64编码的加密字符串，格式为 "salt:iv:ciphertext:tag"
        
        异常:
            EncryptionError: 加密失败时抛出
        
        示例:
            >>> encrypted = service.encrypt("sensitive-api-key")
            >>> print(encrypted)
            "dGVzdC1zYWx0...:dGVzdC1pdi4uLg==:dGVzdC1jaXBoZXJ0ZXh0...:dGVzdC10YWc="
        """
        if not plaintext:
            return ""
        
        try:
            # 生成随机盐和IV
            salt = os.urandom(self.SALT_SIZE)
            iv = os.urandom(self.IV_SIZE)
            
            # 派生加密密钥
            key = self._derive_key(salt)
            
            # 创建AES-GCM加密器
            aesgcm = AESGCM(key)
            
            # 加密数据
            ciphertext = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
            
            # 分离密文和认证标签（GCM模式会自动附加认证标签）
            # GCM模式：ciphertext = encrypted_data + tag
            # tag长度固定为16字节
            tag = ciphertext[-16:]
            encrypted_data = ciphertext[:-16]
            
            # Base64编码各部分
            salt_b64 = base64.b64encode(salt).decode("utf-8")
            iv_b64 = base64.b64encode(iv).decode("utf-8")
            data_b64 = base64.b64encode(encrypted_data).decode("utf-8")
            tag_b64 = base64.b64encode(tag).decode("utf-8")
            
            # 组合为加密字符串
            encrypted = f"{salt_b64}:{iv_b64}:{data_b64}:{tag_b64}"
            
            return encrypted
            
        except Exception as e:
            raise EncryptionError(f"加密失败: {str(e)}") from e
    
    def decrypt(self, encrypted: str) -> str:
        """
        解密加密数据
        
        从Base64编码的加密字符串中解密出明文数据。
        
        参数:
            encrypted: Base64编码的加密字符串，格式为 "salt:iv:ciphertext:tag"
        
        返回:
            解密后的明文数据
        
        异常:
            EncryptionError: 解密失败时抛出（格式错误、密钥错误等）
        
        示例:
            >>> decrypted = service.decrypt("dGVzdC1zYWx0...:dGVzdC1pdi4uLg==:...")
            >>> print(decrypted)
            "sensitive-api-key"
        """
        if not encrypted:
            return ""
        
        try:
            # 解析加密字符串
            parts = encrypted.split(":")
            if len(parts) != 4:
                raise EncryptionError("加密字符串格式错误，应为 'salt:iv:ciphertext:tag'")
            
            salt_b64, iv_b64, data_b64, tag_b64 = parts
            
            # Base64解码
            salt = base64.b64decode(salt_b64)
            iv = base64.b64decode(iv_b64)
            encrypted_data = base64.b64decode(data_b64)
            tag = base64.b64decode(tag_b64)
            
            # 派生解密密钥
            key = self._derive_key(salt)
            
            # 组合密文和认证标签
            ciphertext = encrypted_data + tag
            
            # 创建AES-GCM解密器
            aesgcm = AESGCM(key)
            
            # 解密数据
            plaintext = aesgcm.decrypt(iv, ciphertext, None)
            
            return plaintext.decode("utf-8")
            
        except Exception as e:
            raise EncryptionError(f"解密失败: {str(e)}") from e
    
    def is_encrypted(self, value: str) -> bool:
        """
        检查值是否为加密格式
        
        检查字符串是否符合加密格式（包含4个冒号分隔的Base64部分）。
        
        参数:
            value: 要检查的值
        
        返回:
            True表示是加密格式，False表示是明文
        """
        if not value or not isinstance(value, str):
            return False
        
        parts = value.split(":")
        if len(parts) != 4:
            return False
        
        # 检查每个部分是否为有效的Base64编码
        try:
            for part in parts:
                base64.b64decode(part)
            return True
        except Exception:
            return False
