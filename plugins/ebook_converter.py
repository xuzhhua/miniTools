"""
电子书转换与翻译插件
支持格式：PDF, EPUB, MOBI, TXT
功能：格式转换、OCR识别、AI翻译
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List
import os
import subprocess
import json
import requests
from pathlib import Path
import config


class EbookConverterPlugin(BasePlugin):
    """电子书转换与翻译工具插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "EbookConverter"
        self.version = "1.0.0"
        self.description = "电子书格式转换、OCR识别和AI翻译"
        
        # 支持的格式
        self.supported_formats = ['pdf', 'epub', 'mobi', 'txt', 'azw3', 'docx']
        
        # 翻译进度跟踪 {file_name: {current: int, total: int, status: str}}
        self.translation_progress = {}
        
        # 翻译进度跟踪 {file_path: {current: int, total: int, status: str}}
        self.translation_progress = {}
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "action",
                "type": "string",
                "required": True,
                "description": "操作类型: check_dependencies(检查依赖), convert(格式转换), ocr(OCR识别), translate(翻译), info(获取信息)"
            },
            {
                "name": "input_file",
                "type": "string",
                "required": False,
                "description": "输入文件路径"
            },
            {
                "name": "output_format",
                "type": "string",
                "required": False,
                "description": "输出格式: pdf, epub, mobi, txt等"
            },
            {
                "name": "output_file",
                "type": "string",
                "required": False,
                "description": "输出文件名"
            },
            {
                "name": "use_ocr",
                "type": "boolean",
                "required": False,
                "description": "是否使用OCR识别(针对扫描版PDF)"
            },
            {
                "name": "translate_provider",
                "type": "string",
                "required": False,
                "description": "翻译服务提供商: ollama, deepseek"
            },
            {
                "name": "translate_model",
                "type": "string",
                "required": False,
                "description": "翻译模型名称"
            },
            {
                "name": "target_language",
                "type": "string",
                "required": False,
                "description": "目标语言: zh-CN(简体中文), en(英文)等"
            },
            {
                "name": "bilingual",
                "type": "boolean",
                "required": False,
                "description": "是否生成双语对照版本"
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行插件功能"""
        if params is None:
            params = {}
        
        action = params.get("action", "").lower()
        
        if action == "check_dependencies":
            return self._check_dependencies()
        elif action == "convert":
            return self._convert_format(params)
        elif action == "ocr":
            return self._ocr_process(params)
        elif action == "translate":
            return self._translate_ebook(params)
        elif action == "get_progress":
            return self._get_translation_progress(params)
        elif action == "info":
            return self._get_ebook_info(params)
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {action}"
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """检查依赖工具是否安装"""
        dependencies = {}
        
        # 检查Calibre (ebook-convert)
        try:
            result = subprocess.run(
                ["ebook-convert", "--version"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5
            )
            dependencies["calibre"] = {
                "installed": result.returncode == 0,
                "version": result.stdout.split('\n')[0] if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            dependencies["calibre"] = {"installed": False, "version": None}
        
        # 检查Tesseract OCR
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5
            )
            dependencies["tesseract"] = {
                "installed": result.returncode == 0,
                "version": result.stdout.split('\n')[0] if result.returncode == 0 else None
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            dependencies["tesseract"] = {"installed": False, "version": None}
        
        # 检查Ollama
        try:
            ollama_url = getattr(config, 'OLLAMA_BASE_URL', 'http://localhost:11434')
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            dependencies["ollama"] = {
                "installed": response.status_code == 200,
                "available": response.status_code == 200,
                "models": [m["name"] for m in response.json().get("models", [])] if response.status_code == 200 else []
            }
        except:
            dependencies["ollama"] = {"installed": False, "available": False, "models": []}
        
        return {
            "success": True,
            "dependencies": dependencies
        }
    
    def _convert_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """转换电子书格式"""
        input_file = params.get("input_file")
        output_format = params.get("output_format", "epub")
        output_file = params.get("output_file")
        use_ocr = params.get("use_ocr", False)
        
        if not input_file or not os.path.exists(input_file):
            return {"success": False, "error": "输入文件不存在"}
        
        # 生成输出文件名（使用原文件名）
        if not output_file:
            input_path = Path(input_file)
            output_file = f"{input_path.stem}.{output_format}"
        
        output_path = os.path.join("outputs", output_file)
        os.makedirs("outputs", exist_ok=True)
        
        try:
            # 使用Calibre的ebook-convert进行转换
            cmd = ["ebook-convert", input_file, output_path]
            
            if use_ocr:
                cmd.extend(["--enable-heuristics"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output_file": output_file,
                    "output_path": output_path,
                    "message": "转换成功"
                }
            else:
                return {
                    "success": False,
                    "error": f"转换失败: {result.stderr}"
                }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "未找到ebook-convert工具，请先安装Calibre"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "转换超时，文件可能过大"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"转换失败: {str(e)}"
            }
    
    def _ocr_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """OCR处理扫描版PDF"""
        input_file = params.get("input_file")
        output_format = params.get("output_format", "pdf")
        output_file = params.get("output_file")
        
        if not input_file or not os.path.exists(input_file):
            return {"success": False, "error": "输入文件不存在"}
        
        try:
            # 使用OCRmyPDF进行OCR处理
            if not output_file:
                input_path = Path(input_file)
                output_file = f"{input_path.stem}_ocr.pdf"
            
            output_path = os.path.join("outputs", output_file)
            os.makedirs("outputs", exist_ok=True)
            
            cmd = [
                "ocrmypdf",
                "-l", "chi_sim+eng",  # 简体中文和英文
                "--force-ocr",
                input_file,
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                # 如果需要转换为其他格式
                if output_format != "pdf":
                    return self._convert_format({
                        "input_file": output_path,
                        "output_format": output_format,
                        "output_file": output_file.replace(".pdf", f".{output_format}")
                    })
                
                return {
                    "success": True,
                    "output_file": output_file,
                    "output_path": output_path,
                    "message": "OCR处理成功"
                }
            else:
                return {
                    "success": False,
                    "error": f"OCR处理失败: {result.stderr}"
                }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "未找到ocrmypdf工具，请先安装OCRmyPDF"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR处理失败: {str(e)}"
            }
    
    def _get_translation_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取翻译进度"""
        file_name = params.get("file_name")
        
        if not file_name:
            return {"success": False, "error": "未提供文件名"}
        
        # 添加调试日志
        print(f"查询翻译进度 - 文件名: {file_name}")
        print(f"当前进度数据: {self.translation_progress}")
        
        progress = self.translation_progress.get(file_name, {
            "current": 0,
            "total": 0,
            "status": "not_started"
        })
        
        return {
            "success": True,
            "progress": progress
        }
    
    def _translate_ebook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """翻译电子书"""
        input_file = params.get("input_file")
        provider = params.get("translate_provider", "ollama")
        model = params.get("translate_model", "qwen2.5:7b")
        target_language = params.get("target_language", "zh-CN")
        bilingual = params.get("bilingual", True)
        output_format = params.get("output_format", "epub")
        
        if not input_file or not os.path.exists(input_file):
            return {"success": False, "error": "输入文件不存在"}
        
        # 初始化进度跟踪
        file_name = os.path.basename(input_file)
        self.translation_progress[file_name] = {
            "current": 0,
            "total": 0,
            "status": "starting"
        }
        print(f"开始翻译 - 文件名: {file_name}")
        print(f"初始化进度: {self.translation_progress[file_name]}")
        
        try:
            # 1. 先提取文本内容
            text_content = self._extract_text(input_file)
            if not text_content:
                return {"success": False, "error": "无法提取文本内容，文件可能为空或格式不支持"}
            
            # 2. 翻译文本
            success, result = self._translate_text(
                text_content, 
                provider, 
                model, 
                target_language,
                file_name,
                bilingual  # 传递bilingual参数
            )
            
            if not success:
                return {"success": False, "error": f"翻译失败: {result}"}
            
            # 3. 生成输出文件
            input_path = Path(input_file)
            if bilingual:
                output_file = f"{input_path.stem}_bilingual.{output_format}"
                # result 是 list of (original, translated) tuples
                final_content = self._create_bilingual_content_from_pairs(result)
            else:
                output_file = f"{input_path.stem}_translated.{output_format}"
                # result 是翻译后的文本字符串
                final_content = result
            
            output_path = os.path.join("outputs", output_file)
            os.makedirs("outputs", exist_ok=True)
            
            # 4. 保存为指定格式
            self._save_as_format(final_content, output_path, output_format)
            
            return {
                "success": True,
                "output_file": output_file,
                "output_path": output_path,
                "message": "翻译成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"翻译失败: {str(e)}"
            }
    
    def _extract_text(self, file_path: str) -> str:
        """从电子书中提取文本"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_ext == '.epub':
                return self._extract_epub_text(file_path)
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 尝试转换为txt后提取
                temp_txt = "temp_extract.txt"
                self._convert_format({
                    "input_file": file_path,
                    "output_format": "txt",
                    "output_file": temp_txt
                })
                temp_path = os.path.join("outputs", temp_txt)
                if os.path.exists(temp_path):
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    os.remove(temp_path)
                    return content
                return ""
        except Exception as e:
            print(f"提取文本失败: {str(e)}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """从PDF提取文本"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except:
            return ""
    
    def _extract_epub_text(self, file_path: str) -> str:
        """从EPUB提取文本"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            book = epub.read_epub(file_path)
            text = ""
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text += soup.get_text() + "\n"
            
            return text
        except:
            return ""
    
    def _translate_text(self, text: str, provider: str, model: str, target_language: str, file_name: str = None, bilingual: bool = False) -> tuple:
        """使用AI翻译文本
        返回: (success, result_or_error)
        如果bilingual=True，返回(success, list_of_tuples) 每个tuple为(original_para, translated_para)
        """
        if provider == "ollama":
            return self._translate_with_ollama(text, model, target_language, file_name, bilingual)
        elif provider == "deepseek":
            return self._translate_with_deepseek(text, model, target_language, file_name, bilingual)
        else:
            return (False, "不支持的翻译服务")
    
    def _translate_with_ollama(self, text: str, model: str, target_language: str, file_name: str = None, bilingual: bool = False) -> tuple:
        """使用Ollama翻译
        返回: (success, result_or_error)
        如果bilingual=True，返回(success, list_of_tuples)
        """
        try:
            # 首先按段落分割原文
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            # 使用配置的分段大小
            max_segment_length = getattr(config, 'OLLAMA_MAX_SEGMENT_LENGTH', 2000)
            
            # 将每个段落进一步分割为更小的segments（如果段落太长）
            all_segments = []  # [(para_index, segment_text)]
            for para_idx, para in enumerate(paragraphs):
                if len(para) <= max_segment_length:
                    all_segments.append((para_idx, para))
                else:
                    # 将长段落分割为多个segment
                    sentences = para.split('. ')
                    current_segment = ""
                    for sentence in sentences:
                        if len(current_segment) + len(sentence) + 2 <= max_segment_length:
                            current_segment += sentence + ". "
                        else:
                            if current_segment:
                                all_segments.append((para_idx, current_segment.strip()))
                            current_segment = sentence + ". "
                    if current_segment:
                        all_segments.append((para_idx, current_segment.strip()))
            
            # 更新进度：设置总段落数
            if file_name and file_name in self.translation_progress:
                self.translation_progress[file_name]["total"] = len(all_segments)
                self.translation_progress[file_name]["status"] = "translating"
            
            lang_map = {
                "zh-CN": "简体中文",
                "en": "English",
                "ja": "日本語",
                "ko": "한국어"
            }
            target_lang_name = lang_map.get(target_language, "简体中文")
            
            ollama_url = getattr(config, 'OLLAMA_BASE_URL', 'http://localhost:11434')
            ollama_timeout = getattr(config, 'OLLAMA_API_TIMEOUT', 300)
            max_retries = 2  # 最大重试次数
            
            # 用于存储每个段落的翻译结果
            paragraph_translations = {}  # {para_index: [translated_segments]}
            
            for i, (para_idx, segment) in enumerate(all_segments, 1):
                prompt = f"请将以下文本翻译成{target_lang_name}，保持原文的格式和段落结构，只返回翻译结果：\n\n{segment}"
                
                # 重试机制
                retry_count = 0
                success = False
                
                while retry_count <= max_retries:
                    try:
                        response = requests.post(
                            f"{ollama_url}/api/generate",
                            json={
                                "model": model,
                                "prompt": prompt,
                                "stream": False
                            },
                            timeout=ollama_timeout
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            translated_text = result.get("response", "")
                            if translated_text:
                                # 按段落索引存储翻译结果
                                if para_idx not in paragraph_translations:
                                    paragraph_translations[para_idx] = []
                                paragraph_translations[para_idx].append(translated_text)
                                
                                print(f"  ✓ 段落 {i}/{len(all_segments)} 翻译成功")
                                
                                # 更新进度
                                if file_name and file_name in self.translation_progress:
                                    self.translation_progress[file_name]["current"] = i
                                
                                success = True
                                break  # 成功后退出重试循环
                            else:
                                return (False, f"Ollama返回空结果 (段落 {i}/{len(all_segments)})")
                        else:
                            return (False, f"Ollama API错误: HTTP {response.status_code} - {response.text[:200]}")
                    except requests.exceptions.ConnectionError:
                        # 连接错误不重试，立即返回
                        return (False, f"无法连接到Ollama服务 ({ollama_url})，请确认服务已启动")
                    except requests.exceptions.Timeout:
                        retry_count += 1
                        if retry_count <= max_retries:
                            print(f"  ⚠ Ollama请求超时 (段落 {i}/{len(all_segments)})，第 {retry_count} 次重试...")
                        else:
                            return (False, f"Ollama请求超时 (段落 {i}/{len(all_segments)})，已重试 {max_retries} 次仍然失败。请尝试：1)增加config.py中OLLAMA_API_TIMEOUT至600秒 2)减小OLLAMA_MAX_SEGMENT_LENGTH至500")
                
                # 检查是否成功
                if not success:
                    return (False, f"翻译段落 {i}/{len(all_segments)} 失败")
            
            # 合并翻译结果
            if bilingual:
                # 返回段落对应列表
                bilingual_pairs = []
                for para_idx, para in enumerate(paragraphs):
                    translated_parts = paragraph_translations.get(para_idx, [])
                    translated_para = " ".join(translated_parts) if translated_parts else para
                    bilingual_pairs.append((para, translated_para))
                
                # 更新进度为完成
                if file_name and file_name in self.translation_progress:
                    self.translation_progress[file_name]["status"] = "completed"
                
                return (True, bilingual_pairs)
            else:
                # 按段落顺序合并翻译结果
                translated_paragraphs = []
                for para_idx in sorted(paragraph_translations.keys()):
                    translated_parts = paragraph_translations[para_idx]
                    translated_paragraphs.append(" ".join(translated_parts))
                
                if not translated_paragraphs:
                    return (False, "翻译结果为空")
                
                # 更新进度为完成
                if file_name and file_name in self.translation_progress:
                    self.translation_progress[file_name]["status"] = "completed"
                
                return (True, "\n\n".join(translated_paragraphs))
        except Exception as e:
            # 更新进度为失败
            if file_name and file_name in self.translation_progress:
                self.translation_progress[file_name]["status"] = "failed"
            
            error_msg = f"Ollama翻译异常: {type(e).__name__} - {str(e)}"
            print(error_msg)
            return (False, error_msg)
    
    def _translate_with_deepseek(self, text: str, model: str, target_language: str, file_name: str = None, bilingual: bool = False) -> tuple:
        """使用DeepSeek翻译
        返回: (success, result_or_error)
        如果bilingual=True，返回(success, list_of_tuples)
        """
        try:
            # 获取API密钥：优先使用config中的配置，其次使用环境变量
            api_key = getattr(config, 'DEEPSEEK_API_KEY', '') or os.environ.get("DEEPSEEK_API_KEY", "")
            if not api_key:
                return (False, "未配置DeepSeek API密钥，请在config.py中设置DEEPSEEK_API_KEY或设置环境变量")
            
            deepseek_url = getattr(config, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
            deepseek_timeout = getattr(config, 'DEEPSEEK_API_TIMEOUT', 120)
            
            # 首先按段落分割原文
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            # 将每个段落进一步分割为更小的segments（如果段落太长）
            max_segment_length = 2000
            all_segments = []  # [(para_index, segment_text)]
            for para_idx, para in enumerate(paragraphs):
                if len(para) <= max_segment_length:
                    all_segments.append((para_idx, para))
                else:
                    # 将长段落分割为多个segment
                    sentences = para.split('. ')
                    current_segment = ""
                    for sentence in sentences:
                        if len(current_segment) + len(sentence) + 2 <= max_segment_length:
                            current_segment += sentence + ". "
                        else:
                            if current_segment:
                                all_segments.append((para_idx, current_segment.strip()))
                            current_segment = sentence + ". "
                    if current_segment:
                        all_segments.append((para_idx, current_segment.strip()))
            
            # 更新进度：设置总段落数
            if file_name and file_name in self.translation_progress:
                self.translation_progress[file_name]["total"] = len(all_segments)
                self.translation_progress[file_name]["status"] = "translating"
            
            lang_map = {
                "zh-CN": "简体中文",
                "en": "English",
                "ja": "日本語",
                "ko": "한국어"
            }
            target_lang_name = lang_map.get(target_language, "简体中文")
            
            # 用于存储每个段落的翻译结果
            paragraph_translations = {}  # {para_index: [translated_segments]}
            
            for i, (para_idx, segment) in enumerate(all_segments, 1):
                try:
                    response = requests.post(
                        f"{deepseek_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model or "deepseek-chat",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"请将以下文本翻译成{target_lang_name}，保持原文的格式和段落结构，只返回翻译结果：\n\n{segment}"
                                }
                            ]
                        },
                        timeout=deepseek_timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        translated_text = result["choices"][0]["message"]["content"]
                        if translated_text:
                            # 按段落索引存储翻译结果
                            if para_idx not in paragraph_translations:
                                paragraph_translations[para_idx] = []
                            paragraph_translations[para_idx].append(translated_text)
                            
                            print(f"  ✓ 段落 {i}/{len(all_segments)} 翻译成功")
                            
                            # 更新进度
                            if file_name and file_name in self.translation_progress:
                                self.translation_progress[file_name]["current"] = i
                        else:
                            return (False, f"DeepSeek返回空结果 (段落 {i}/{len(all_segments)})")
                    else:
                        error_detail = response.text[:200]
                        return (False, f"DeepSeek API错误: HTTP {response.status_code} - {error_detail}")
                except requests.exceptions.Timeout:
                    return (False, f"DeepSeek请求超时 (段落 {i}/{len(all_segments)})，请检查网络或增加超时时间")
                except requests.exceptions.ConnectionError:
                    return (False, f"无法连接到DeepSeek服务 ({deepseek_url})，请检查网络连接")
            
            # 合并翻译结果
            if bilingual:
                # 返回段落对应列表
                bilingual_pairs = []
                for para_idx, para in enumerate(paragraphs):
                    translated_parts = paragraph_translations.get(para_idx, [])
                    translated_para = " ".join(translated_parts) if translated_parts else para
                    bilingual_pairs.append((para, translated_para))
                
                # 更新进度为完成
                if file_name and file_name in self.translation_progress:
                    self.translation_progress[file_name]["status"] = "completed"
                
                return (True, bilingual_pairs)
            else:
                # 按段落顺序合并翻译结果
                translated_paragraphs = []
                for para_idx in sorted(paragraph_translations.keys()):
                    translated_parts = paragraph_translations[para_idx]
                    translated_paragraphs.append(" ".join(translated_parts))
                
                if not translated_paragraphs:
                    return (False, "翻译结果为空")
                
                # 更新进度为完成
                if file_name and file_name in self.translation_progress:
                    self.translation_progress[file_name]["status"] = "completed"
                
                return (True, "\n\n".join(translated_paragraphs))
        except KeyError as e:
            # 更新进度为失败
            if file_name and file_name in self.translation_progress:
                self.translation_progress[file_name]["status"] = "failed"
            
            error_msg = f"DeepSeek API响应格式错误: 缺少字段 {str(e)}"
            print(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"DeepSeek翻译异常: {type(e).__name__} - {str(e)}"
            print(error_msg)
            return (False, error_msg)
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """分割文本为多个段落"""
        # 按段落分割
        paragraphs = text.split('\n\n')
        segments = []
        current_segment = ""
        
        for para in paragraphs:
            if len(current_segment) + len(para) < max_length:
                current_segment += para + "\n\n"
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = para + "\n\n"
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def _create_bilingual_content(self, original: str, translated: str) -> str:
        """创建双语对照内容（旧版本，保留兼容）"""
        original_paras = original.split('\n\n')
        translated_paras = translated.split('\n\n')
        
        bilingual = []
        for i in range(max(len(original_paras), len(translated_paras))):
            if i < len(original_paras):
                bilingual.append(original_paras[i])
            if i < len(translated_paras):
                bilingual.append(translated_paras[i])
            bilingual.append("")  # 空行分隔
        
        return "\n".join(bilingual)
    
    def _create_bilingual_content_from_pairs(self, paragraph_pairs: list) -> str:
        """从段落对创建双语对照内容
        Args:
            paragraph_pairs: list of (original_para, translated_para) tuples
        Returns:
            双语对照的文本内容
        """
        bilingual = []
        for original, translated in paragraph_pairs:
            bilingual.append(original)  # 原文
            bilingual.append(translated)  # 译文
            bilingual.append("")  # 空行分隔
        
        return "\n".join(bilingual)
    
    def _save_as_format(self, content: str, output_path: str, format: str):
        """保存内容为指定格式"""
        if format == "txt":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # 先保存为txt，然后转换
            temp_txt = output_path.replace(f".{format}", ".txt")
            with open(temp_txt, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 使用ebook-convert转换
            subprocess.run(
                ["ebook-convert", temp_txt, output_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120
            )
            
            if os.path.exists(temp_txt):
                os.remove(temp_txt)
    
    def _get_ebook_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取电子书信息"""
        input_file = params.get("input_file")
        
        if not input_file or not os.path.exists(input_file):
            return {"success": False, "error": "输入文件不存在"}
        
        try:
            file_path = Path(input_file)
            file_stat = os.stat(input_file)
            
            info = {
                "filename": file_path.name,
                "format": file_path.suffix.lower().replace('.', ''),
                "size": f"{file_stat.st_size / (1024*1024):.2f} MB",
                "path": input_file
            }
            
            # 尝试提取更多信息
            if file_path.suffix.lower() == '.epub':
                info.update(self._get_epub_metadata(input_file))
            elif file_path.suffix.lower() == '.pdf':
                info.update(self._get_pdf_metadata(input_file))
            
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取信息失败: {str(e)}"
            }
    
    def _get_epub_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取EPUB元数据"""
        try:
            import ebooklib
            from ebooklib import epub
            
            book = epub.read_epub(file_path)
            return {
                "title": book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "未知",
                "author": book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "未知",
                "language": book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "未知"
            }
        except:
            return {}
    
    def _get_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取PDF元数据"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                info = pdf_reader.metadata
                
                return {
                    "title": info.get('/Title', '未知') if info else '未知',
                    "author": info.get('/Author', '未知') if info else '未知',
                    "pages": len(pdf_reader.pages)
                }
        except:
            return {}
