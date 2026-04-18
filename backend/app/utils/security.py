import hashlib
import hmac
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime, timedelta
import secrets

# 密钥管理
SECRET_KEY = "your-secret-key-for-encryption"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# AES-256加密
class AESCipher:
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.iv = secrets.token_bytes(16)  # 初始化向量
    
    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(self.iv + encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        encrypted_data = base64.b64decode(encrypted_data)
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return decrypted.decode('utf-8')

# 生成签名
def generate_signature(data, secret):
    signature = hmac.new(secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

# 验证签名
def verify_signature(data, signature, secret):
    expected_signature = generate_signature(data, secret)
    return hmac.compare_digest(signature, expected_signature)

# 生成随机令牌
def generate_token(length=32):
    return secrets.token_hex(length)

# 数据脱敏
def mask_sensitive_data(data, field):
    if field in data:
        value = str(data[field])
        if len(value) > 4:
            data[field] = value[:2] + '*' * (len(value) - 4) + value[-2:]
    return data

# 验证密码强度
def validate_password_strength(password):
    if len(password) < 8:
        return False, "密码长度至少为8位"
    if not any(char.isdigit() for char in password):
        return False, "密码必须包含数字"
    if not any(char.isupper() for char in password):
        return False, "密码必须包含大写字母"
    if not any(char.islower() for char in password):
        return False, "密码必须包含小写字母"
    return True, "密码强度符合要求"