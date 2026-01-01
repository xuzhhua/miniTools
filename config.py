"""
配置文件
"""

# HTTP服务配置
HOST = '0.0.0.0'  # 监听所有网络接口
PORT = 18787

# 插件目录
PLUGIN_DIR = 'plugins'

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 电子书转换工具配置
# Ollama配置
OLLAMA_BASE_URL = 'http://localhost:11434'  # Ollama服务地址
OLLAMA_API_TIMEOUT = 300  # Ollama API请求超时时间（秒），建议300-600秒用于长文本翻译
OLLAMA_MAX_SEGMENT_LENGTH = 1000  # 每段最大字符数（默认2000，减小可提高稳定性但增加请求次数）

# DeepSeek配置
DEEPSEEK_API_KEY = ''  # DeepSeek API密钥，留空则从环境变量DEEPSEEK_API_KEY读取
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'  # DeepSeek API地址
DEEPSEEK_API_TIMEOUT = 120  # DeepSeek API请求超时时间（秒）
