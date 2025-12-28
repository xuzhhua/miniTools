"""
示例插件 - 系统信息工具
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List
import platform
import os
from datetime import datetime


class SystemInfoPlugin(BasePlugin):
    """系统信息工具插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "SystemInfo"
        self.version = "1.0.0"
        self.description = "获取系统信息"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "info_type",
                "type": "string",
                "required": False,
                "description": "信息类型: all(全部), os(操作系统), python(Python版本), time(当前时间)",
                "default": "all"
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取系统信息"""
        if params is None:
            params = {}
        
        info_type = params.get("info_type", "all").lower()
        
        try:
            result = {}
            
            if info_type in ["all", "os"]:
                result["os"] = {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                }
            
            if info_type in ["all", "python"]:
                result["python"] = {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "compiler": platform.python_compiler()
                }
            
            if info_type in ["all", "time"]:
                now = datetime.now()
                result["time"] = {
                    "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": now.timestamp()
                }
            
            if info_type == "all":
                result["environment"] = {
                    "user": os.environ.get("USERNAME") or os.environ.get("USER"),
                    "home": os.path.expanduser("~"),
                    "cwd": os.getcwd()
                }
            
            if not result:
                return {
                    "success": False,
                    "data": None,
                    "message": f"不支持的信息类型: {info_type}"
                }
            
            return {
                "success": True,
                "data": result,
                "message": "获取系统信息成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"获取系统信息失败: {str(e)}"
            }
