"""
示例插件 - 文本处理工具
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List


class TextToolPlugin(BasePlugin):
    """文本处理工具插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "TextTool"
        self.version = "1.0.0"
        self.description = "提供文本处理功能，包括大小写转换、反转、统计等"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "text",
                "type": "string",
                "required": True,
                "description": "要处理的文本"
            },
            {
                "name": "operation",
                "type": "string",
                "required": True,
                "description": "操作类型: uppercase(大写), lowercase(小写), reverse(反转), count(统计)"
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行文本处理"""
        if params is None:
            params = {}
        
        text = params.get("text", "")
        operation = params.get("operation", "").lower()
        
        try:
            if operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "reverse":
                result = text[::-1]
            elif operation == "count":
                result = {
                    "length": len(text),
                    "words": len(text.split()),
                    "lines": len(text.splitlines())
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"不支持的操作: {operation}"
                }
            
            return {
                "success": True,
                "data": result,
                "message": "处理成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"处理失败: {str(e)}"
            }
