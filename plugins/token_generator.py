"""
Token生成器插件
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List
import uuid
import secrets
import string
import hashlib
import time
import base64


class TokenGeneratorPlugin(BasePlugin):
    """Token生成器插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "TokenGenerator"
        self.version = "1.0.0"
        self.description = "生成各种类型的Token，包括UUID、随机字符串、API密钥等"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "token_type",
                "type": "string",
                "required": True,
                "description": "Token类型: uuid4, uuid1, hex(十六进制), base64, alphanumeric(字母数字), api_key, secure(高安全), timestamp"
            },
            {
                "name": "length",
                "type": "int",
                "required": False,
                "description": "Token长度（仅适用于hex/base64/alphanumeric/api_key/secure类型），默认32",
                "default": 32
            },
            {
                "name": "count",
                "type": "int",
                "required": False,
                "description": "生成Token数量，默认1",
                "default": 1
            },
            {
                "name": "prefix",
                "type": "string",
                "required": False,
                "description": "Token前缀（可选）",
                "default": ""
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行Token生成"""
        if params is None:
            params = {}
        
        try:
            token_type = params.get("token_type", "").lower()
            length = int(params.get("length", 32))
            count = int(params.get("count", 1))
            prefix = params.get("prefix", "")
            
            # 限制生成数量
            if count < 1 or count > 100:
                return {
                    "success": False,
                    "data": None,
                    "message": "生成数量必须在1-100之间"
                }
            
            # 限制长度
            if length < 1 or length > 256:
                return {
                    "success": False,
                    "data": None,
                    "message": "长度必须在1-256之间"
                }
            
            tokens = []
            for _ in range(count):
                if token_type == "uuid4":
                    token = str(uuid.uuid4())
                elif token_type == "uuid1":
                    token = str(uuid.uuid1())
                elif token_type == "hex":
                    token = secrets.token_hex(length // 2)
                elif token_type == "base64":
                    token = secrets.token_urlsafe(length)[:length]
                elif token_type == "alphanumeric":
                    token = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                                  for _ in range(length))
                elif token_type == "api_key":
                    # API密钥格式：sk_前缀 + 随机字符
                    random_part = secrets.token_hex(length // 2)
                    token = f"sk_{random_part}"
                elif token_type == "secure":
                    # 高安全token：包含大小写字母、数字和特殊字符
                    chars = string.ascii_letters + string.digits + "!@#$%^&*"
                    token = ''.join(secrets.choice(chars) for _ in range(length))
                elif token_type == "timestamp":
                    # 时间戳token
                    timestamp = str(int(time.time() * 1000))
                    random_part = secrets.token_hex(8)
                    token = f"{timestamp}_{random_part}"
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": f"不支持的Token类型: {token_type}。支持的类型: uuid4, uuid1, hex, base64, alphanumeric, api_key, secure, timestamp"
                    }
                
                # 添加前缀
                if prefix:
                    token = f"{prefix}{token}"
                
                tokens.append(token)
            
            # 构建结果
            result = {
                "tokens": tokens,
                "type": token_type,
                "count": count,
                "length": len(tokens[0]) if tokens else 0
            }
            
            # 如果只有一个token，额外提供单个token字段
            if count == 1:
                result["token"] = tokens[0]
            
            return {
                "success": True,
                "data": result,
                "message": f"成功生成 {count} 个Token"
            }
            
        except ValueError as e:
            return {
                "success": False,
                "data": None,
                "message": f"参数格式错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"生成Token失败: {str(e)}"
            }
