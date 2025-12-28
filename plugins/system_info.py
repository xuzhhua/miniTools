"""
示例插件 - 系统信息工具
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List
import platform
import os
from datetime import datetime
import psutil
import subprocess


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
                "description": "信息类型: all(全部), os(操作系统), cpu(处理器), python(Python版本), time(当前时间)",
                "default": "all"
            }
        ]
    
    def _get_os_release(self) -> str:
        """获取准确的操作系统版本（Windows 11检测）"""
        try:
            if platform.system() == "Windows":
                # 使用 platform.win32_ver() 获取版本号
                release, version, csd, ptype = platform.win32_ver()
                # Windows 11 的版本号是 10.0.22000 或更高
                if version:
                    build = version.split('.')[-1] if '.' in version else version
                    try:
                        build_num = int(build)
                        if build_num >= 22000:
                            return "11"
                    except:
                        pass
                return release
            else:
                return platform.release()
        except:
            return platform.release()
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """获取详细的CPU信息"""
        cpu_info = {}
        
        try:
            # CPU名称/型号
            processor = platform.processor() or "未知"
            
            # 在Windows上尝试从注册表获取更友好的CPU名称
            cpu_name = self._get_cpu_name_from_registry() or processor
            
            cpu_info["model"] = cpu_name
            if cpu_name != processor:
                cpu_info["model_technical"] = processor  # 保留技术型号
            
            # 物理核心数
            cpu_info["physical_cores"] = psutil.cpu_count(logical=False)
            
            # 逻辑核心数（包括超线程）
            cpu_info["logical_cores"] = psutil.cpu_count(logical=True)
            
            # CPU频率（统一使用GHz格式）
            freq = psutil.cpu_freq()
            if freq:
                cpu_info["frequency"] = {
                    "current": f"{freq.current / 1000:.2f} GHz",
                    "min": f"{freq.min / 1000:.2f} GHz" if freq.min else "未知",
                    "max": f"{freq.max / 1000:.2f} GHz" if freq.max else "未知"
                }
            else:
                cpu_info["frequency"] = {
                    "current": "未知",
                    "min": "未知",
                    "max": "未知"
                }
            
            # 每个核心的使用率
            per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_info["per_core_usage"] = [f"{usage:.1f}%" for usage in per_cpu]
            
        except Exception as e:
            cpu_info["error"] = f"获取CPU信息失败: {str(e)}"
        
        return cpu_info
    
    def _get_cpu_name_from_registry(self) -> str:
        """从Windows注册表获取CPU名称"""
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                winreg.CloseKey(key)
                return cpu_name.strip()
        except Exception:
            pass
        return None
    
    def _get_architecture(self) -> str:
        """获取易读的系统架构（64位/32位）"""
        machine = platform.machine().lower()
        if 'amd64' in machine or 'x86_64' in machine or 'arm64' in machine:
            return "64位"
        elif 'i386' in machine or 'i686' in machine or 'x86' in machine:
            return "32位"
        else:
            return machine
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        try:
            mem = psutil.virtual_memory()
            return {
                "total": f"{mem.total / (1024**3):.2f} GB",
                "available": f"{mem.available / (1024**3):.2f} GB",
                "used": f"{mem.used / (1024**3):.2f} GB",
                "percent": f"{mem.percent}%"
            }
        except Exception as e:
            return {"error": f"获取内存信息失败: {str(e)}"}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """获取显卡信息"""
        gpu_info = {}
        try:
            # 尝试使用nvidia-smi获取NVIDIA显卡信息
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].split(',')
                    if len(parts) >= 2:
                        gpu_info["model"] = parts[0].strip()
                        memory_str = parts[1].strip()
                        try:
                            memory_mb = float(memory_str.split()[0])
                            memory_gb = round(memory_mb / 1024, 1)
                            gpu_info["memory"] = f"{memory_gb} GB"
                        except:
                            gpu_info["memory"] = memory_str
                        return gpu_info
            
            # 如果nvidia-smi失败，返回基本信息
            gpu_info["model"] = "未检测到独立显卡或驱动未安装"
            return gpu_info
            
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            gpu_info["model"] = "未检测到独立显卡或驱动未安装"
            return gpu_info
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取系统信息"""
        if params is None:
            params = {}
        
        info_type = params.get("info_type", "all").lower()
        
        try:
            result = {}
            
            if info_type in ["all", "os"]:
                os_info = {
                    "system": platform.system(),
                    "release": self._get_os_release(),
                    "version": platform.version(),
                    "architecture": self._get_architecture(),
                    "memory": self._get_memory_info(),
                    "gpu": self._get_gpu_info()
                }
                result["os"] = os_info
            
            # 添加详细的CPU信息
            if info_type in ["all", "cpu"]:
                result["cpu"] = self._get_cpu_info()
            
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
