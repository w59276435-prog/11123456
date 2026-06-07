"""安全认证和加密工具

JWT 令牌管理、密码哈希、数据加密
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ==================== 密码哈希 ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT Token ====================

class JWTManager:
    """JWT 令牌管理器"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_expire_minutes
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            raise
    
    def decode_token(self, token: str) -> Dict:
        """解码 JWT 令牌"""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token decode failed: {str(e)}")
            raise
    
    def verify_token(self, token: str, token_type: str = "access") -> bool:
        """验证令牌有效性"""
        try:
            payload = self.decode_token(token)
            if payload.get("type") != token_type:
                return False
            return True
        except JWTError:
            return False


jwt_manager = JWTManager()


# ==================== 数据加密 ====================

class EncryptionManager:
    """数据加密管理器 - AES-256"""
    
    def __init__(self, key: Optional[str] = None):
        if key is None:
            key = settings.pi_enc_key
        
        # 确保密钥长度为 32 字节 (256 bits)
        if len(key) < 32:
            key = key.ljust(32, '0')
        elif len(key) > 32:
            key = key[:32]
        
        key_bytes = key.encode()
        encoded_key = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
        self.cipher = Fernet(encoded_key)
    
    def encrypt(self, plaintext: str) -> str:
        """加密字符串"""
        try:
            if not plaintext:
                return ""
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """解密字符串"""
        try:
            if not ciphertext:
                return ""
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise


encryption_manager = EncryptionManager()
