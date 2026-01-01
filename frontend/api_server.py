"""
前台HTTP API服务
提供RESTful API接口
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import os
import tempfile
from typing import Dict, Any
from backend.plugin_manager import PluginManager
from werkzeug.utils import secure_filename


logger = logging.getLogger(__name__)


class APIServer:
    """API服务器"""
    
    def __init__(self, plugin_manager: PluginManager, host: str = '0.0.0.0', port: int = 8080):
        self.app = Flask(__name__)
        CORS(self.app)  # 允许跨域请求
        self.plugin_manager = plugin_manager
        self.host = host
        self.port = port
        
        # 获取项目根目录和静态文件夹
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.static_folder = os.path.join(self.project_root, 'static')
        
        # 创建临时文件夹用于存储上传的文件
        self.upload_folder = os.path.join(self.project_root, 'uploads')
        self.output_folder = os.path.join(self.project_root, 'outputs')
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)
        
        # 配置Flask - 增加文件上传限制到2GB
        self.app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB 最大上传
        self.app.config['UPLOAD_FOLDER'] = self.upload_folder
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        """注册所有路由"""
        
        @self.app.route('/', methods=['GET'])
        def index():
            """主页 - 重定向到统一工具界面"""
            return self.app.redirect('/ui')
        
        @self.app.route('/ui', methods=['GET'])
        def tools_home():
            """统一工具界面"""
            try:
                html_path = os.path.join(self.static_folder, 'index.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载主页失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/api', methods=['GET'])
        def api_info():
            """API信息"""
            return jsonify({
                "service": "MiniTools API",
                "version": "1.0.0",
                "endpoints": {
                    "GET /": "主页（重定向到/ui）",
                    "GET /ui": "统一工具界面",
                    "GET /ui/calculator": "计算器Web界面",
                    "GET /ui/token": "Token生成器Web界面",
                    "GET /ui/text": "文本处理Web界面",
                    "GET /ui/system": "系统信息Web界面",
                    "GET /api": "API信息",
                    "GET /plugins": "获取所有插件列表",
                    "GET /plugins/<name>": "获取指定插件信息",
                    "POST /plugins/<name>/execute": "执行指定插件",
                    "POST /plugins/reload": "重新加载所有插件"
                }
            })
        
        @self.app.route('/ui/calculator', methods=['GET'])
        def calculator_ui():
            """计算器Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'calculator.html')
                logger.info(f"尝试加载文件: {html_path}")
                logger.info(f"文件是否存在: {os.path.exists(html_path)}")
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载计算器界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/ui/text', methods=['GET'])
        def text_tool_ui():
            """文本处理工具Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'text_tool.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载文本处理界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/ui/system', methods=['GET'])
        def system_info_ui():
            """系统信息工具Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'system_info.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载系统信息界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/ui/token', methods=['GET'])
        def token_ui():
            """Token生成器Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'token_generator.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载Token生成器界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/ui/json', methods=['GET'])
        def json_formatter_ui():
            """JSON格式化工具Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'json_formatter.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载JSON格式化工具界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/ui/video', methods=['GET'])
        def video_compressor_ui():
            """视频压缩工具Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'video_compressor.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载视频压缩工具界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/ui/ebook', methods=['GET'])
        def ebook_converter_ui():
            """电子书转换工具Web界面"""
            try:
                html_path = os.path.join(self.static_folder, 'ebook_converter.html')
                
                if not os.path.exists(html_path):
                    return jsonify({
                        "success": False,
                        "message": f"文件不存在: {html_path}"
                    }), 404
                
                return send_file(html_path)
            except Exception as e:
                logger.error(f"加载电子书转换工具界面失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"页面加载失败: {str(e)}"
                }), 500
        
        @self.app.route('/plugins', methods=['GET'])
        def list_plugins():
            """获取所有插件列表"""
            try:
                plugins = self.plugin_manager.list_plugins()
                return jsonify({
                    "success": True,
                    "data": plugins,
                    "count": len(plugins)
                })
            except Exception as e:
                logger.error(f"获取插件列表失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 500
        
        @self.app.route('/plugins/<plugin_name>', methods=['GET'])
        def get_plugin_info(plugin_name: str):
            """获取指定插件信息"""
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if not plugin:
                return jsonify({
                    "success": False,
                    "message": f"插件不存在: {plugin_name}"
                }), 404
            
            return jsonify({
                "success": True,
                "data": plugin.get_info()
            })
        
        @self.app.route('/plugins/<plugin_name>/execute', methods=['POST'])
        def execute_plugin(plugin_name: str):
            """执行指定插件"""
            try:
                # 获取请求参数
                params = request.get_json() if request.is_json else {}
                
                # 执行插件
                result = self.plugin_manager.execute_plugin(plugin_name, params)
                
                status_code = 200 if result.get("success") else 400
                return jsonify(result), status_code
                
            except Exception as e:
                logger.error(f"执行插件失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 500
        
        @self.app.route('/plugins/reload', methods=['POST'])
        def reload_plugins():
            """重新加载所有插件"""
            try:
                self.plugin_manager.reload_plugins()
                return jsonify({
                    "success": True,
                    "message": "插件重新加载成功",
                    "count": len(self.plugin_manager.plugins)
                })
            except Exception as e:
                logger.error(f"重新加载插件失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 500
        
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            """上传文件"""
            try:
                if 'file' not in request.files:
                    return jsonify({
                        "success": False,
                        "error": "没有文件上传"
                    }), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({
                        "success": False,
                        "error": "未选择文件"
                    }), 400
                
                # 保存文件
                filename = secure_filename(file.filename)
                filepath = os.path.join(self.upload_folder, filename)
                file.save(filepath)
                
                return jsonify({
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "size": os.path.getsize(filepath)
                })
            
            except Exception as e:
                logger.error(f"文件上传失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/video/info', methods=['POST'])
        def get_video_info():
            """获取视频信息"""
            try:
                data = request.get_json()
                filepath = data.get('filepath')
                
                if not filepath or not os.path.exists(filepath):
                    return jsonify({
                        "success": False,
                        "error": "文件不存在"
                    }), 400
                
                result = self.plugin_manager.execute_plugin('VideoCompressor', {
                    'action': 'get_info',
                    'input_file': filepath
                })
                
                return jsonify(result)
            
            except Exception as e:
                logger.error(f"获取视频信息失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/video/compress', methods=['POST'])
        def compress_video():
            """压缩视频"""
            try:
                data = request.get_json()
                input_file = data.get('input_file')
                output_filename = data.get('output_filename', 'compressed_video.mp4')
                
                if not input_file or not os.path.exists(input_file):
                    return jsonify({
                        "success": False,
                        "error": "输入文件不存在"
                    }), 400
                
                # 构建输出文件路径
                output_file = os.path.join(self.output_folder, output_filename)
                
                # 执行压缩
                result = self.plugin_manager.execute_plugin('VideoCompressor', {
                    'action': 'compress',
                    'input_file': input_file,
                    'output_file': output_file,
                    'encoder': data.get('encoder', 'auto'),
                    'resolution': data.get('resolution', 'original'),
                    'bitrate': data.get('bitrate', '2M'),
                    'preset': data.get('preset', 'medium'),
                    'crf': data.get('crf', 23)
                })
                
                return jsonify(result)
            
            except Exception as e:
                logger.error(f"视频压缩失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/download/<filename>', methods=['GET'])
        def download_file(filename):
            """下载文件"""
            try:
                filepath = os.path.join(self.output_folder, secure_filename(filename))
                if not os.path.exists(filepath):
                    return jsonify({
                        "success": False,
                        "error": "文件不存在"
                    }), 404
                
                return send_file(filepath, as_attachment=True, download_name=filename)
            
            except Exception as e:
                logger.error(f"文件下载失败: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            """404错误处理"""
            return jsonify({
                "success": False,
                "message": "接口不存在"
            }), 404
        
        @self.app.errorhandler(413)
        def request_entity_too_large(error):
            """413错误处理 - 文件过大"""
            return jsonify({
                "success": False,
                "error": "文件太大，最大支持2GB"
            }), 413
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """500错误处理"""
            return jsonify({
                "success": False,
                "message": "服务器内部错误"
            }), 500
    
    def run(self, debug: bool = False):
        """启动服务器"""
        logger.info(f"启动API服务器: http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)
