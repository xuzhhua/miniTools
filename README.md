# MiniTools - 统一工具管理平台

一个插件化的工具管理系统，提供HTTP API接口和Web界面，支持远程访问和扩展。

## 特性

- 🔌 **插件化架构**: 易于添加新工具，只需继承BasePlugin类
- 🌐 **HTTP API**: 提供RESTful API接口，支持远程调用
- 🖥️ **Web界面**: 为每个插件提供友好的Web操作界面
- 🔄 **热重载**: 支持动态重新加载插件，无需重启服务
- 📝 **参数验证**: 自动验证插件参数
- 🛡️ **跨域支持**: 支持CORS，便于前端集成
- 📦 **文件处理**: 支持大文件上传（最大2GB）

## 项目结构

```
miniTools/
├── backend/              # 后台模块
│   ├── __init__.py
│   ├── base_plugin.py    # 插件基类
│   └── plugin_manager.py # 插件管理器
├── frontend/             # 前台模块
│   ├── __init__.py
│   └── api_server.py     # HTTP API服务
├── plugins/              # 插件目录
│   ├── __init__.py
│   ├── calculator.py     # 计算器工具
│   ├── text_tool.py      # 文本处理工具
│   ├── system_info.py    # 系统信息工具
│   ├── token_generator.py# 令牌生成器
│   ├── json_formatter.py # JSON格式化工具
│   ├── video_compressor.py# 视频压缩工具
│   └── ebook_converter.py# 电子书转换工具
├── static/               # 静态文件（Web界面）
│   ├── index.html        # 主页
│   ├── calculator.html
│   ├── text_tool.html
│   ├── system_info.html
│   ├── token_generator.html
│   ├── json_formatter.html
│   ├── video_compressor.html
│   └── ebook_converter.html
├── uploads/              # 上传文件目录
├── outputs/              # 输出文件目录
├── config.py             # 配置文件
├── main.py               # 主程序入口
├── requirements.txt      # 依赖列表
└── README.md            # 说明文档
```

## 已实现的插件

### 1. 计算器 (Calculator)
- 基本算术运算：加、减、乘、除
- Web界面：实时计算显示

### 2. 文本处理工具 (TextTool)
- 大小写转换（大写、小写、首字母大写）
- 文本统计（字符数、单词数、行数）
- 文本反转
- Web界面：多功能文本操作

### 3. 系统信息 (SystemInfo)
- **操作系统信息**：
  - 准确识别Windows 11等系统版本
  - 架构显示（64位/32位）
  - 内存信息（总量、可用、已用及使用率）
  - 显卡信息（型号和显存容量）
- **CPU详细信息**：
  - 处理器型号（从系统注册表获取友好名称）
  - 物理核心数和逻辑核心数
  - 实时频率显示（统一使用GHz格式）
  - 每个核心的独立使用率
- **Python环境信息**：版本、实现、编译器
- **环境信息**：用户、主目录、当前目录
- Web界面：实时系统监控，信息一键复制

### 4. 令牌生成器 (TokenGenerator)
- UUID生成（v1, v4）
- 随机令牌生成（指定长度）
- 时间戳令牌
- JWT风格令牌（Base64编码）
- Web界面：多种令牌快速生成

### 5. JSON格式化工具 (JsonFormatter)
- JSON格式化（美化）
- JSON压缩（移除空格）
- JSON验证
- 语法高亮显示
- Web界面：实时格式化和验证

### 6. 视频压缩工具 (VideoCompressor) ⭐
- **GPU加速**: 支持NVIDIA NVENC、AMD VCE、Intel QSV
- **显卡信息**: 自动检测并显示显卡型号和显存容量
- **多种质量选择**: 7级质量（极低、低、中低、标准、中高、高、超高）
- **分辨率调整**: 支持原始、1080p、720p、480p、360p
- **编码速度**: 快速、中等、慢速（更高质量）
- **智能预估**: 实时预估压缩后文件大小、处理时间和压缩比
- **大文件支持**: 支持最大2GB视频文件上传
- **进度显示**: 实时显示上传和处理进度
- Web界面：完整的视频压缩流程

### 7. 电子书转换与翻译 (EbookConverter) ⭐⭐
- **格式转换**：
  - 支持格式：PDF、EPUB、MOBI、TXT、AZW3、DOCX
  - 使用Calibre的ebook-convert进行高质量转换
  - 批量转换支持
- **OCR识别**：
  - 扫描版PDF文字识别
  - 支持中英文混合识别
  - 使用Tesseract OCR引擎
  - 自动生成可搜索的PDF
- **AI翻译**：
  - 支持Ollama本地翻译（完全免费）
  - 支持DeepSeek云端翻译（需API密钥）
  - 双语对照模式（原文+译文段落对照）
  - 纯译文模式
  - 支持多种语言：简体中文、英文、日文、韩文
  - **配置说明**: 详见 [EBOOK_CONFIG.md](EBOOK_CONFIG.md)
  - **错误排查**: 详见 [TRANSLATION_ERROR_FIX.md](TRANSLATION_ERROR_FIX.md)
- **元数据提取**：自动提取书名、作者、页数、语言等信息
- Web界面：直观的三标签页设计（格式转换、OCR、翻译）

## 安装

### 前置依赖

1. **Python 3.7+**
2. **psutil** (系统信息获取，自动安装)
3. **FFmpeg** (视频压缩功能必需)
   - Windows: 从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载并添加到PATH
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
4. **nvidia-smi** (可选，用于NVIDIA显卡信息显示)
   - 随NVIDIA显卡驱动自动安装5. **Calibre** (电子书转换功能必需)
   - Windows: 从 [Calibre官网](https://calibre-ebook.com/download) 下载安装
   - Linux: `sudo apt install calibre`
   - macOS: `brew install calibre`
6. **Tesseract OCR** (扫描版PDF识别功能可选)
   - **安装指南**: 详见 [TESSERACT_GUIDE.md](TESSERACT_GUIDE.md)
   - Windows: 从 [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装,安装时选择中文语言包
   - Linux: `sudo apt install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng`
   - macOS: `brew install tesseract tesseract-lang`
7. **OCRmyPDF** (扫描版PDF识别功能可选)
   - 安装命令: `pip install ocrmypdf`
8. **Ollama** (本地AI翻译功能可选)
   - 从 [Ollama官网](https://ollama.ai/) 下载安装
   - 安装后运行: `ollama pull qwen:7b` 或其他支持的模型
### 安装步骤

1. 克隆或下载本项目

2. 安装Python依赖：
```bash
pip install -r requirements.txt
```

3. 创建必要的目录：
```bash
mkdir uploads outputs
```

## 使用

### 启动服务

```bash
python main.py
```

服务将在 `http://0.0.0.0:18787` 启动

### 访问Web界面

在浏览器中打开：`http://localhost:18787`

您将看到主页，列出所有可用的工具插件。点击任何工具即可使用其Web界面。

### API接口

#### 1. 获取API信息
```
GET /
返回主页HTML
```

#### 2. 获取所有插件列表
```
GET /plugins
```

响应示例：
```json
{
  "success": true,
  "data": [
    {
      "name": "TextTool",
      "version": "1.0.0",
      "description": "提供文本处理功能",
      "parameters": [...]
    }
  ],
  "count": 6
}
```

#### 3. 获取指定插件信息
```
GET /plugins/<plugin_name>
```

#### 4. 执行插件
```
POST /plugins/<plugin_name>/execute
Content-Type: application/json

{
  "param1": "value1",
  "param2": "value2"
}
```

#### 5. 重新加载插件
```
POST /plugins/reload
```

#### 6. 文件上传 (用于视频压缩)
```
POST /upload
Content-Type: multipart/form-data

file: <视频文件>
```

#### 7. 视频压缩
```
POST /video/compress
Content-Type: application/json

{
  "input_file": "uploads/video.mp4",
  "output_filename": "compressed.mp4",
  "encoder": "auto",
  "resolution": "1280x720",
  "quality": "medium",
  "preset": "medium"
}
```

#### 8. 获取视频信息
```
POST /video/info
Content-Type: application/json

{
  "filepath": "uploads/video.mp4"
}
```

#### 9. 下载文件
```
GET /download/<filename>
```

### 使用示例

#### 通过Web界面（推荐）

直接访问 `http://localhost:18787` 使用各个工具的图形界面。

#### 通过API调用

##### 文本处理工具
```bash
# 转大写
curl -X POST http://localhost:18787/plugins/TextTool/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "operation": "uppercase"}'

# 统计文本
curl -X POST http://localhost:18787/plugins/TextTool/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "operation": "count"}'
```

##### 计算器工具
```bash
curl -X POST http://localhost:18787/plugins/Calculator/execute \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5, "operation": "add"}'
```

##### 系统信息工具
```bash
curl -X POST http://localhost:18787/plugins/SystemInfo/execute \
  -H "Content-Type: application/json" \
  -d '{"info_type": "all"}'
```

##### 令牌生成器
```bash
curl -X POST http://localhost:18787/plugins/TokenGenerator/execute \
  -H "Content-Type: application/json" \
  -d '{"token_type": "uuid4"}'
```

##### JSON格式化工具
```bash
curl -X POST http://localhost:18787/plugins/JsonFormatter/execute \
  -H "Content-Type: application/json" \
  -d '{"json_text": "{\"name\":\"test\"}", "operation": "format"}'
```

##### 视频压缩工具
```bash
# 检测GPU
curl -X POST http://localhost:18787/plugins/VideoCompressor/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "check_gpu"}'

# 获取视频信息
curl -X POST http://localhost:18787/video/info \
  -H "Content-Type: application/json" \
  -d '{"filepath": "uploads/video.mp4"}'
```

##### 电子书转换工具
```bash
# 检查依赖
curl -X POST http://localhost:18787/plugins/EbookConverter/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "check_dependencies"}'

# 格式转换
curl -X POST http://localhost:18787/plugins/EbookConverter/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "convert", "input_file": "uploads/book.epub", "output_format": "pdf"}'

# OCR识别
curl -X POST http://localhost:18787/plugins/EbookConverter/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "ocr", "input_file": "uploads/scanned.pdf"}'

# AI翻译（Ollama本地翻译）
curl -X POST http://localhost:18787/plugins/EbookConverter/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "translate",
    "input_file": "uploads/book.epub",
    "target_language": "zh-CN",
    "translator": "ollama",
    "model": "qwen:7b",
    "bilingual": true,
    "output_format": "txt"
  }'

# AI翻译（DeepSeek云端翻译）
curl -X POST http://localhost:18787/plugins/EbookConverter/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "translate",
    "input_file": "uploads/book.pdf",
    "target_language": "zh-CN",
    "translator": "deepseek",
    "api_key": "your-deepseek-api-key",
    "bilingual": false,
    "output_format": "pdf"
  }'
```

## 开发新插件

### 1. 创建插件文件

在 `plugins/` 目录下创建新的Python文件，例如 `my_tool.py`

### 2. 继承BasePlugin类

```python
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List


class MyToolPlugin(BasePlugin):
    """我的工具插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "MyTool"
        self.version = "1.0.0"
        self.description = "我的工具描述"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "input",
                "type": "string",
                "required": True,
                "description": "输入参数"
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行插件功能"""
        if params is None:
            params = {}
        
        # 处理逻辑
        result = f"处理结果: {params.get('input')}"
        
        return {
            "success": True,
            "data": result,
            "message": "执行成功"
        }
```

### 3. 重新加载插件

无需重启服务，调用重载接口：
```bash
curl -X POST http://localhost:18787/plugins/reload
```

## 视频压缩工具详细说明

### 功能特性

1. **GPU硬件加速**
   - 自动检测并优先使用GPU编码器
   - 支持 NVIDIA NVENC（h264_nvenc）
   - 支持 AMD VCE（h264_amf）
   - 支持 Intel Quick Sync（h264_qsv）
   - 降级方案：CPU编码（libx264）

2. **显卡信息显示**
   - 自动检测NVIDIA显卡型号（如：NVIDIA GeForce RTX 3060）
   - 显示显存容量（如：12 GB）
   - 适用于NVIDIA显卡，需要nvidia-smi工具

3. **7级质量选择**
   - 极低质量：500kbps（预览用，文件极小）
   - 低质量：1Mbps（快速分享）
   - 中低质量：1.5Mbps（节省空间）
   - 标准质量：2Mbps（推荐）
   - 中高质量：3Mbps（清晰度好）
   - 高质量：5Mbps（较大文件）
   - 超高质量：8Mbps（接近原画）

4. **分辨率调整**
   - 保持原始分辨率
   - 1080p (1920x1080)
   - 720p (1280x720)
   - 480p (854x480)
   - 360p (640x360)

5. **编码速度预设**
   - 快速：处理速度快，文件稍大
   - 中等：平衡速度和质量（推荐）
   - 慢速：处理较慢，质量更好

6. **智能预估**
   - 实时预估压缩后文件大小
   - 预估处理时间（考虑GPU加速）
   - 显示压缩比例
   - 参数调整时自动更新预估

### 使用流程

1. 打开视频压缩工具页面
2. 查看显卡信息（确认硬件加速支持）
3. 选择或拖拽视频文件上传
4. 等待视频信息加载和预估计算
5. 根据需求调整参数：
   - 输出文件名
   - 编码器（推荐使用"自动选择"）
   - 分辨率
   - 视频质量
   - 编码速度
6. 查看预估信息（文件大小、处理时间、压缩比）
7. 点击"开始压缩"
8. 等待处理完成
9. 下载压缩后的视频

### 系统要求

- **FFmpeg**: 必须安装并添加到系统PATH
- **存储空间**: 至少预留3倍于原视频大小的空间
- **内存**: 建议4GB以上
- **GPU驱动**: 
  - NVIDIA显卡需要安装最新驱动
  - AMD显卡需要安装最新驱动
  - Intel显卡需要支持Quick Sync

### 常见问题

**Q: 为什么检测不到GPU？**
A: 请确保：
- 已安装最新显卡驱动
- FFmpeg版本支持对应的GPU编码器
- 显卡硬件支持视频编码功能

**Q: 文件上传失败？**
A: 检查：
- 文件是否超过2GB（当前限制）
- 磁盘空间是否充足
- 文件是否为有效的视频格式

**Q: 压缩很慢？**
A: 可能原因：
- 未使用GPU加速（检查编码器选择）
- 选择了"慢速"编码预设
- 原视频分辨率或码率很高
- CPU性能不足（使用GPU可显著提升速度）

**Q: 压缩后质量不满意？**
A: 建议：
- 提高质量等级
- 保持原始分辨率
- 使用"慢速"编码预设以获得更好质量

## 电子书转换工具详细说明

### 功能特性

1. **格式转换**
   - 支持格式：PDF、EPUB、MOBI、TXT、AZW3、DOCX
   - 基于Calibre的ebook-convert引擎，转换质量高
   - 保留书籍元数据（书名、作者、封面等）
   - 自动调整排版和格式

2. **OCR文字识别**
   - 扫描版PDF转可搜索PDF
   - 支持中英文混合识别（chi_sim + eng）
   - 基于Tesseract OCR引擎
   - 使用OCRmyPDF工具，保持原PDF格式
   - 识别后的PDF可复制、搜索文字
   - 处理进度显示

3. **AI智能翻译**
   - **两种翻译引擎**：
     - Ollama（本地翻译，完全免费，需安装）
     - DeepSeek（云端翻译，需API密钥）
   - **支持语言**：简体中文、英语、日语、韩语
   - **两种输出模式**：
     - 双语对照：原文和译文段落对照显示
     - 纯译文：仅输出翻译后的文本
   - **智能分段**：
     - 自动将长文本分段翻译（2000字符/段）
     - 保持段落结构和换行
     - 进度实时显示
   - **多格式输出**：支持输出为TXT或PDF格式

4. **依赖检测**
   - 自动检测Calibre安装状态和版本
   - 自动检测Tesseract OCR安装状态
   - 自动检测Ollama服务状态
   - 列出Ollama可用模型列表
   - 在Web界面显示依赖安装状态

### 使用流程

#### 格式转换
1. 打开电子书转换工具页面
2. 切换到"格式转换"标签
3. 选择或拖拽电子书文件上传
4. 选择目标格式（PDF、EPUB、MOBI、TXT、AZW3、DOCX）
5. 点击"开始转换"
6. 等待处理完成（通常几秒到几分钟）
7. 点击下载链接获取转换后的文件

#### OCR识别
1. 切换到"OCR识别"标签
2. 上传扫描版PDF文件
3. 点击"开始OCR识别"
4. 等待处理完成（时间取决于页数和清晰度）
5. 下载可搜索的PDF文件

#### AI翻译
1. 切换到"AI翻译"标签
2. 上传电子书文件（PDF、EPUB、TXT等）
3. 选择翻译引擎：
   - **Ollama（推荐新手）**：
     - 选择"Ollama（本地翻译）"
     - 从模型列表中选择（推荐qwen系列）
     - 完全免费，数据不上传云端
   - **DeepSeek（推荐快速翻译）**：
     - 选择"DeepSeek（云端翻译）"
     - 输入DeepSeek API密钥
     - 翻译速度快，质量高
4. 选择目标语言（通常选择"简体中文"）
5. 选择翻译模式：
   - 双语对照：原文和译文对照显示（推荐）
   - 仅翻译文本：只输出译文
6. 选择输出格式（TXT或PDF）
7. 点击"开始翻译"
8. 等待处理完成（长文本可能需要较长时间）
9. 下载翻译后的文件

### 系统要求

#### 必需依赖
- **Python 3.7+**
- **Flask及相关包**（自动安装）
- **Python包**（运行pip install -r requirements.txt自动安装）：
  - PyPDF2（PDF处理）
  - ebooklib（EPUB处理）
  - beautifulsoup4（HTML解析）
  - Pillow（图像处理）
  - requests（HTTP请求）

#### 格式转换依赖
- **Calibre**（必需）：
  - Windows: 从[官网](https://calibre-ebook.com/download)下载安装
  - Linux: `sudo apt install calibre`
  - macOS: `brew install calibre`
  - 确保ebook-convert命令在PATH中

#### OCR识别依赖（可选）
- **Tesseract OCR**：
  - **详细安装指南**: [TESSERACT_GUIDE.md](TESSERACT_GUIDE.md)
  - Windows: 从[UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)下载安装
    - 安装时选择"中文简体"和"English"语言包
  - Linux: `sudo apt install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng`
  - macOS: `brew install tesseract tesseract-lang`
- **OCRmyPDF**：
  - 安装: `pip install ocrmypdf`

#### AI翻译依赖（可选）
- **Ollama**（本地翻译）：
  - 从[官网](https://ollama.ai/)下载安装
  - 安装后运行: `ollama pull qwen:7b`（或其他模型）
  - 推荐模型：qwen:7b、qwen:14b、llama2:13b
- **DeepSeek API**（云端翻译）：
  - 注册[DeepSeek账号](https://platform.deepseek.com/)
  - 获取API密钥
  - 设置环境变量（可选）：`DEEPSEEK_API_KEY=your-key`

### 常见问题

**Q: 转换失败，提示找不到ebook-convert？**
A: 请确保：
- 已正确安装Calibre
- Calibre的安装路径已添加到系统PATH
- Windows用户：通常路径为`C:\Program Files\Calibre2\`

**Q: OCR识别失败？**
A: 检查：
- 是否已安装Tesseract OCR
- 是否已安装中文语言包（chi_sim）
- 是否已安装ocrmypdf：`pip install ocrmypdf`
- PDF是否为扫描版（如果已是文字版，无需OCR）

**Q: Ollama翻译失败？**
A: 可能原因：
- Ollama服务未启动（运行`ollama serve`）
- 模型未下载（运行`ollama pull qwen:7b`）
- 模型名称错误（从依赖检测中查看可用模型）

**Q: DeepSeek翻译失败？**
A: 请确保：
- API密钥正确
- 账户余额充足
- 网络连接正常

**Q: 翻译很慢？**
A: 这是正常现象：
- 长文本需要分段翻译
- Ollama本地翻译速度取决于CPU/GPU性能
- DeepSeek云端翻译速度取决于网络和API限流
- 建议：先用短文本测试，长文本耐心等待

**Q: 翻译质量不好？**
A: 建议：
- Ollama用户：尝试更大的模型（qwen:14b、llama2:13b）
- DeepSeek用户：已使用先进模型，质量较高
- 检查原文是否清晰（OCR识别的文本可能有错误）

**Q: 支持哪些电子书格式？**
A: 
- **读取**：PDF、EPUB、MOBI、AZW3、TXT、DOCX
- **转换输出**：PDF、EPUB、MOBI、TXT、AZW3、DOCX
- **OCR输入**：仅PDF
- **翻译输出**：TXT、PDF

**Q: 如何选择翻译引擎？**
A:
- **Ollama优势**：完全免费、数据本地处理、不限次数
- **Ollama劣势**：需要下载模型（几GB）、翻译较慢、需要较好的硬件
- **DeepSeek优势**：速度快、质量高、无需本地资源
- **DeepSeek劣势**：需要API密钥、可能有费用、需要网络

## 配置

在 [config.py](config.py) 中修改配置：

### 基础配置
```python
HOST = '0.0.0.0'      # 服务监听地址
PORT = 18787          # 服务端口
PLUGIN_DIR = 'plugins' # 插件目录
```

### 电子书转换工具配置
```python
# Ollama配置
OLLAMA_BASE_URL = 'http://localhost:11434'  # Ollama服务地址
OLLAMA_API_TIMEOUT = 120  # API请求超时时间（秒）

# DeepSeek配置
DEEPSEEK_API_KEY = ''  # DeepSeek API密钥
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'  # DeepSeek API地址
DEEPSEEK_API_TIMEOUT = 120  # API请求超时时间（秒）
```

详细配置说明请参考: [EBOOK_CONFIG.md](EBOOK_CONFIG.md)

### 文件上传限制

在 [api_server.py](frontend/api_server.py) 中修改：

```python
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 最大上传2GB
```

## 扩展性设计

### 插件自动发现
- 系统自动扫描plugins目录
- 自动加载所有BasePlugin子类
- 支持热重载

### 统一接口规范
- 所有插件继承BasePlugin
- 统一的参数定义和验证
- 统一的返回格式

### 便利性功能
- 参数自动验证
- 错误自动处理
- 日志自动记录
- Web界面自动生成（可选）

## 技术栈

### 后端
- Python 3.7+
- Flask 3.0.0 - Web框架
- Flask-CORS 4.0.0 - 跨域支持
- psutil - 系统信息获取

### 前端
- 原生 HTML/CSS/JavaScript
- 渐变色设计
- 响应式布局
- Fetch API

### 视频处理
- FFmpeg - 视频编码/解码
- nvidia-smi - NVIDIA GPU信息（可选）
- 支持多种GPU编码器

## 贡献

欢迎提交Issue和Pull Request！

开发新插件的步骤：
1. 在 `plugins/` 目录创建插件文件
2. 继承 `BasePlugin` 类
3. 实现 `get_parameters()` 和 `execute()` 方法
4. （可选）在 `static/` 目录创建对应的HTML界面
5. 调用 `/plugins/reload` 接口重新加载

## 许可

MIT License

---

## 更新日志

### v1.4.0 (2025-12-31)
- 📚 新增电子书转换与翻译工具（EbookConverter）
- 🔄 格式转换：支持PDF、EPUB、MOBI、TXT、AZW3、DOCX互转
- 👁️ OCR识别：扫描版PDF文字识别，支持中英文混合
- 🤖 AI翻译：集成Ollama和DeepSeek，支持双语对照模式
- 📖 双语对照：原文和译文段落对照显示
- 🌍 多语言支持：简体中文、英语、日语、韩语
- ⚙️ 依赖检测：自动检测Calibre、Tesseract、Ollama状态
- 🎨 三标签页界面：格式转换、OCR识别、AI翻译独立操作

### v1.3.0 (2025-12-28)
- 🎮 优化显卡信息显示，支持显示NVIDIA显卡型号和显存容量
- 📊 改进GPU状态展示，只显示主力显卡的详细信息
- 💻 修复Windows 11版本识别问题，准确显示系统版本
- ⚡ 增强CPU信息显示：
  - 从注册表获取友好的CPU型号名称
  - 显示物理核心数和逻辑核心数
  - 统一使用GHz格式显示CPU频率
  - 移除总体使用率，保留每核心使用率
- 🖥️ 改进操作系统信息显示：
  - 架构显示为易懂的"64位"或"32位"
  - 新增内存信息（总量、可用、已用、使用率）
  - 新增显卡信息（型号和显存）
  - 从操作系统信息中移除处理器字段（改在CPU信息中单独显示）
- 📦 添加psutil依赖以支持详细系统信息

### v1.2.0 (2025-12-28)
- ✨ 新增视频压缩工具实时预估功能
- 📈 显示预估文件大小、处理时间和压缩比
- 🔄 参数调整时自动更新预估信息

### v1.1.0 (2025-12-28)
- 🎯 优化视频压缩质量选择，从4级扩展到7级
- 📝 使用用户友好的质量描述替代技术性码率设置
- 🎨 改进Web界面交互体验

### v1.0.0 (2025-12-28)
- 🎉 初始版本发布
- ✅ 实现6个核心插件（Calculator、TextTool、SystemInfo、TokenGenerator、JsonFormatter、VideoCompressor）
- 🌐 完整的Web界面支持
- 🚀 GPU加速视频压缩功能
