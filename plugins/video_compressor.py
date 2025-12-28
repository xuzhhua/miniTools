import subprocess
import os
import json
from typing import Dict, Any
from backend.base_plugin import BasePlugin

class VideoCompressor(BasePlugin):
    """视频压缩工具插件，支持GPU加速"""
    
    def __init__(self):
        super().__init__()
        self.description = "视频压缩工具，支持GPU加速（NVIDIA NVENC, AMD VCE等）"
        self.version = "1.0.0"
    
    def get_parameters(self):
        """返回插件所需的参数"""
        return [
            {
                "name": "action",
                "type": "string",
                "required": True,
                "description": "操作类型：check_gpu（检测GPU），get_info（获取视频信息），compress（压缩）",
                "enum": ["check_gpu", "get_info", "compress"]
            },
            {
                "name": "input_file",
                "type": "string",
                "required": False,
                "description": "输入视频文件的绝对路径"
            },
            {
                "name": "output_file",
                "type": "string",
                "required": False,
                "description": "输出视频文件的绝对路径"
            },
            {
                "name": "encoder",
                "type": "string",
                "required": False,
                "description": "编码器类型：h264_nvenc（NVIDIA），h264_amf（AMD），h264_qsv（Intel），libx264（CPU）",
                "default": "auto"
            },
            {
                "name": "resolution",
                "type": "string",
                "required": False,
                "description": "目标分辨率，格式：1920x1080",
                "default": "original"
            },
            {
                "name": "bitrate",
                "type": "string",
                "required": False,
                "description": "目标码率，如：2M, 4M, 8M",
                "default": "2M"
            },
            {
                "name": "preset",
                "type": "string",
                "required": False,
                "description": "编码预设：fast, medium, slow",
                "default": "medium"
            },
            {
                "name": "crf",
                "type": "int",
                "required": False,
                "description": "CRF质量参数（0-51，越小质量越高），仅CPU编码",
                "default": 23
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行插件功能"""
        if params is None:
            params = {}
        
        action = params.get("action")
        
        if action == "check_gpu":
            return self._check_gpu()
        elif action == "get_info":
            return self._get_video_info(params.get("input_file"))
        elif action == "compress":
            return self._compress_video(params)
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {action}"
            }
    
    def _check_ffmpeg(self):
        """检查ffmpeg是否安装"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _get_nvidia_gpu_info(self):
        """获取NVIDIA显卡信息（型号和显存）"""
        try:
            # 尝试使用nvidia-smi获取显卡信息
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # 解析输出，格式："GPU Name, Memory MB"
                lines = result.stdout.strip().split('\n')
                if lines:
                    # 取第一张显卡的信息
                    parts = lines[0].split(',')
                    if len(parts) >= 2:
                        gpu_model = parts[0].strip()
                        memory_str = parts[1].strip()
                        # 转换显存单位（MiB 转 GB）
                        try:
                            memory_mb = float(memory_str.split()[0])
                            memory_gb = round(memory_mb / 1024, 1)
                            return {
                                "model": gpu_model,
                                "memory": f"{memory_gb} GB"
                            }
                        except:
                            return {
                                "model": gpu_model,
                                "memory": memory_str
                            }
            return {"model": "未知", "memory": "未知"}
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return {"model": "未知", "memory": "未知"}
    
    def _check_gpu(self):
        """检测可用的GPU编码器并获取显卡信息"""
        if not self._check_ffmpeg():
            return {
                "success": False,
                "error": "未检测到ffmpeg，请先安装 ffmpeg"
            }
        
        try:
            # 获取ffmpeg支持的编码器列表
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            encoders_output = result.stdout
            
            # 获取NVIDIA显卡信息
            nvidia_info = self._get_nvidia_gpu_info()
            
            gpu_encoders = {
                "nvidia": {
                    "available": "h264_nvenc" in encoders_output,
                    "name": "NVIDIA NVENC",
                    "encoder": "h264_nvenc",
                    "gpu_model": nvidia_info.get("model", "未知"),
                    "gpu_memory": nvidia_info.get("memory", "未知")
                },
                "amd": {
                    "available": "h264_amf" in encoders_output,
                    "name": "AMD VCE",
                    "encoder": "h264_amf"
                },
                "intel": {
                    "available": "h264_qsv" in encoders_output,
                    "name": "Intel Quick Sync",
                    "encoder": "h264_qsv"
                },
                "cpu": {
                    "available": "libx264" in encoders_output,
                    "name": "CPU (libx264)",
                    "encoder": "libx264"
                }
            }
            
            return {
                "success": True,
                "ffmpeg_installed": True,
                "encoders": gpu_encoders
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"检测GPU失败: {str(e)}"
            }
    
    def _get_video_info(self, input_file):
        """获取视频信息"""
        if not input_file:
            return {"success": False, "error": "未指定输入文件"}
        
        if not os.path.exists(input_file):
            return {"success": False, "error": f"文件不存在: {input_file}"}
        
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", 
                 "-show_format", "-show_streams", input_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "无法读取视频信息"}
            
            info = json.loads(result.stdout)
            
            # 提取关键信息
            video_stream = next((s for s in info.get("streams", []) if s["codec_type"] == "video"), None)
            audio_stream = next((s for s in info.get("streams", []) if s["codec_type"] == "audio"), None)
            format_info = info.get("format", {})
            
            return {
                "success": True,
                "info": {
                    "filename": os.path.basename(input_file),
                    "size": int(format_info.get("size", 0)),
                    "duration": float(format_info.get("duration", 0)),
                    "bitrate": int(format_info.get("bit_rate", 0)),
                    "video": {
                        "codec": video_stream.get("codec_name") if video_stream else None,
                        "width": video_stream.get("width") if video_stream else None,
                        "height": video_stream.get("height") if video_stream else None,
                        "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream else None
                    },
                    "audio": {
                        "codec": audio_stream.get("codec_name") if audio_stream else None,
                        "channels": audio_stream.get("channels") if audio_stream else None,
                        "sample_rate": audio_stream.get("sample_rate") if audio_stream else None
                    }
                }
            }
        
        except Exception as e:
            return {"success": False, "error": f"获取视频信息失败: {str(e)}"}
    
    def _compress_video(self, params):
        """压缩视频"""
        input_file = params.get("input_file")
        output_file = params.get("output_file")
        
        if not input_file or not output_file:
            return {"success": False, "error": "未指定输入或输出文件"}
        
        if not os.path.exists(input_file):
            return {"success": False, "error": f"输入文件不存在: {input_file}"}
        
        # 确定使用的编码器
        encoder = params.get("encoder", "auto")
        if encoder == "auto":
            gpu_check = self._check_gpu()
            if gpu_check.get("success"):
                encoders = gpu_check.get("encoders", {})
                # 优先级：NVIDIA > AMD > Intel > CPU
                if encoders.get("nvidia", {}).get("available"):
                    encoder = "h264_nvenc"
                elif encoders.get("amd", {}).get("available"):
                    encoder = "h264_amf"
                elif encoders.get("intel", {}).get("available"):
                    encoder = "h264_qsv"
                else:
                    encoder = "libx264"
            else:
                encoder = "libx264"
        
        # 构建ffmpeg命令
        cmd = ["ffmpeg", "-i", input_file]
        
        # 添加编码器参数
        cmd.extend(["-c:v", encoder])
        
        # 分辨率设置
        resolution = params.get("resolution", "original")
        if resolution != "original":
            cmd.extend(["-s", resolution])
        
        # 码率设置
        bitrate = params.get("bitrate", "2M")
        cmd.extend(["-b:v", bitrate])
        
        # 预设设置
        preset = params.get("preset", "medium")
        if encoder in ["h264_nvenc", "h264_amf", "h264_qsv"]:
            # GPU编码器预设
            cmd.extend(["-preset", preset])
        else:
            # CPU编码器
            cmd.extend(["-preset", preset])
            crf = params.get("crf", 23)
            cmd.extend(["-crf", str(crf)])
        
        # 音频编码
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])
        
        # 输出文件
        cmd.extend(["-y", output_file])  # -y 覆盖已存在的文件
        
        try:
            # 执行压缩
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"压缩失败: {result.stderr}"
                }
            
            # 获取输出文件信息
            if os.path.exists(output_file):
                input_size = os.path.getsize(input_file)
                output_size = os.path.getsize(output_file)
                compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0
                
                return {
                    "success": True,
                    "message": "压缩完成",
                    "result": {
                        "output_file": output_file,
                        "input_size": input_size,
                        "output_size": output_size,
                        "compression_ratio": round(compression_ratio, 2),
                        "encoder_used": encoder
                    }
                }
            else:
                return {"success": False, "error": "输出文件未生成"}
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "压缩超时（超过1小时）"}
        except Exception as e:
            return {"success": False, "error": f"压缩过程出错: {str(e)}"}
