"""
主程序入口
"""
import logging
import sys
from backend.plugin_manager import PluginManager
from frontend.api_server import APIServer
import config


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT
    )


def main():
    """主函数"""
    # 配置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("="*50)
        logger.info("MiniTools - 统一工具管理平台")
        logger.info("="*50)
        
        # 初始化插件管理器
        logger.info("初始化插件管理器...")
        plugin_manager = PluginManager(config.PLUGIN_DIR)
        
        # 加载所有插件
        plugin_manager.load_plugins()
        
        # 初始化API服务器
        logger.info("初始化API服务器...")
        api_server = APIServer(plugin_manager, config.HOST, config.PORT)
        
        # 启动服务器
        logger.info("="*50)
        api_server.run(debug=False)
        
    except KeyboardInterrupt:
        logger.info("\n正在关闭服务...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
