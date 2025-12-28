"""
JSON格式化工具插件
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List
import json


class JsonFormatterPlugin(BasePlugin):
    """JSON格式化工具插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "JsonFormatter"
        self.version = "1.0.0"
        self.description = "提供JSON格式化、压缩和验证功能"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "json_text",
                "type": "string",
                "required": True,
                "description": "要处理的JSON文本"
            },
            {
                "name": "operation",
                "type": "string",
                "required": True,
                "description": "操作类型: format(格式化), compress(压缩), validate(验证)"
            },
            {
                "name": "indent",
                "type": "int",
                "required": False,
                "description": "缩进空格数（仅用于format），默认4",
                "default": 4
            },
            {
                "name": "sort_keys",
                "type": "bool",
                "required": False,
                "description": "是否排序键（仅用于format），默认False",
                "default": False
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行JSON处理"""
        if params is None:
            params = {}
        
        try:
            json_text = params.get("json_text", "")
            operation = params.get("operation", "").lower()
            indent = int(params.get("indent", 4))
            sort_keys = bool(params.get("sort_keys", False))
            
            if not json_text.strip():
                return {
                    "success": False,
                    "data": None,
                    "message": "JSON文本不能为空"
                }
            
            # 首先尝试解析JSON
            try:
                json_obj = json.loads(json_text)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "data": None,
                    "message": f"JSON格式错误: {str(e)}"
                }
            
            if operation == "format":
                # 格式化JSON
                result = json.dumps(json_obj, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
                
                return {
                    "success": True,
                    "data": {
                        "result": result,
                        "original_size": len(json_text),
                        "formatted_size": len(result),
                        "keys_count": self._count_keys(json_obj),
                        "depth": self._get_depth(json_obj)
                    },
                    "message": "格式化成功"
                }
                
            elif operation == "compress":
                # 压缩JSON（移除所有空白）
                result = json.dumps(json_obj, separators=(',', ':'), ensure_ascii=False)
                
                return {
                    "success": True,
                    "data": {
                        "result": result,
                        "original_size": len(json_text),
                        "compressed_size": len(result),
                        "compression_ratio": f"{(1 - len(result) / len(json_text)) * 100:.2f}%",
                        "keys_count": self._count_keys(json_obj),
                        "depth": self._get_depth(json_obj)
                    },
                    "message": "压缩成功"
                }
                
            elif operation == "validate":
                # 验证JSON
                return {
                    "success": True,
                    "data": {
                        "valid": True,
                        "type": type(json_obj).__name__,
                        "size": len(json_text),
                        "keys_count": self._count_keys(json_obj),
                        "depth": self._get_depth(json_obj),
                        "structure": self._analyze_structure(json_obj)
                    },
                    "message": "JSON格式正确"
                }
            
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"不支持的操作: {operation}。支持的操作: format, compress, validate"
                }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"处理失败: {str(e)}"
            }
    
    def _count_keys(self, obj: Any, count: int = 0) -> int:
        """递归统计JSON中的键数量"""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self._count_keys(value, count)
        elif isinstance(obj, list):
            for item in obj:
                count = self._count_keys(item, count)
        return count
    
    def _get_depth(self, obj: Any, current_depth: int = 0) -> int:
        """获取JSON的最大深度"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_depth(item, current_depth + 1) for item in obj)
        return current_depth
    
    def _analyze_structure(self, obj: Any) -> Dict[str, int]:
        """分析JSON结构"""
        structure = {
            "objects": 0,
            "arrays": 0,
            "strings": 0,
            "numbers": 0,
            "booleans": 0,
            "nulls": 0
        }
        
        def analyze(item):
            if isinstance(item, dict):
                structure["objects"] += 1
                for value in item.values():
                    analyze(value)
            elif isinstance(item, list):
                structure["arrays"] += 1
                for element in item:
                    analyze(element)
            elif isinstance(item, str):
                structure["strings"] += 1
            elif isinstance(item, (int, float)):
                structure["numbers"] += 1
            elif isinstance(item, bool):
                structure["booleans"] += 1
            elif item is None:
                structure["nulls"] += 1
        
        analyze(obj)
        return structure
