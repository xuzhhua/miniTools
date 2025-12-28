"""
插件基类
所有工具插件都需要继承此类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "插件描述"
    
    @abstractmethod
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行插件功能
        
        Args:
            params: 输入参数字典
            
        Returns:
            执行结果字典，格式: {
                "success": bool,
                "data": Any,
                "message": str
            }
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": self.get_parameters()
        }
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """
        获取插件参数定义
        
        Returns:
            参数列表，格式: [
                {
                    "name": "param_name",
                    "type": "string|int|float|bool",
                    "required": True|False,
                    "description": "参数描述",
                    "default": "默认值"
                }
            ]
        """
        return []
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证参数
        
        Returns:
            (是否有效, 错误信息)
        """
        if params is None:
            params = {}
            
        param_defs = self.get_parameters()
        
        for param_def in param_defs:
            param_name = param_def.get("name")
            required = param_def.get("required", False)
            
            if required and param_name not in params:
                return False, f"缺少必需参数: {param_name}"
        
        return True, ""
