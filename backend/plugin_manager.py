"""
插件管理器
负责插件的加载、管理和执行
"""
import os
import importlib.util
import logging
from typing import Dict, List, Any
from .base_plugin import BasePlugin


logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, BasePlugin] = {}
        
    def load_plugins(self):
        """加载所有插件"""
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return
        
        logger.info(f"开始从 {self.plugin_dir} 加载插件...")
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                self._load_plugin(filename)
        
        logger.info(f"成功加载 {len(self.plugins)} 个插件")
    
    def _load_plugin(self, filename: str):
        """加载单个插件"""
        try:
            plugin_path = os.path.join(self.plugin_dir, filename)
            module_name = filename[:-3]  # 去掉.py后缀
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找BasePlugin的子类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr is not BasePlugin):
                    
                    # 实例化插件
                    plugin_instance = attr()
                    plugin_name = plugin_instance.name
                    self.plugins[plugin_name] = plugin_instance
                    logger.info(f"加载插件: {plugin_name} v{plugin_instance.version}")
                    
        except Exception as e:
            logger.error(f"加载插件 {filename} 失败: {str(e)}")
    
    def get_plugin(self, plugin_name: str) -> BasePlugin:
        """获取指定插件"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件信息"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def execute_plugin(self, plugin_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行插件
        
        Args:
            plugin_name: 插件名称
            params: 执行参数
            
        Returns:
            执行结果
        """
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            return {
                "success": False,
                "data": None,
                "message": f"插件不存在: {plugin_name}"
            }
        
        # 验证参数
        valid, error_msg = plugin.validate_params(params)
        if not valid:
            return {
                "success": False,
                "data": None,
                "message": f"参数验证失败: {error_msg}"
            }
        
        try:
            result = plugin.execute(params)
            logger.info(f"插件 {plugin_name} 执行成功")
            return result
        except Exception as e:
            logger.error(f"插件 {plugin_name} 执行失败: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"执行错误: {str(e)}"
            }
    
    def reload_plugins(self):
        """重新加载所有插件"""
        self.plugins.clear()
        self.load_plugins()
