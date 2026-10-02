import subprocess
import os
import json
from typing import Dict, Any
from backend.base_plugin import BasePlugin

class VideoCompressor(BasePlugin):
    """视频压缩工具插件，支持GPU加速"""
    
    # 支持的编码器定义（preset_option 表示该编码器对应的预设参数名）
    _ENCODERS = {
        "h264_nvenc": {
            "name": "NVIDIA NVENC",
            "preset_option": "-preset",
            "presets": {"fast": "fast", "medium": "medium", "slow": "slow"},
            "pix_fmt": "yuv420p",
        },
        "h264_amf": {
            "name": "AMD VCE",
            "preset_option": "-quality",
            "presets": {"fast": "speed", "medium": "balanced", "slow": "quality"},
            "pix_fmt": "nv12",
        },
        "h264_qsv": {
            "name": "Intel Quick Sync",
            "preset_option": "-preset",
            "presets": {"fast": "veryfast", "medium": "medium", "slow": "slow"},
            "pix_fmt": "nv12",
        },
        "libx264": {
            "name": "CPU (libx264)",
            "preset_option": "-preset",
            "presets": {"fast": "fast", "medium": "medium", "slow": "slow"},
            "pix_fmt": None,
        },
    }
    
    # 自动选择的优先级：NVIDIA > AMD > Intel > CPU
    _AUTO_PRIORITY = ("nvidia", "amd", "intel", "cpu")
    
    def __init__(self):
        super().__init__()
        self.description = "视频压缩工具，支持GPU硬件加速（NVIDIA NVENC / AMD VCE / Intel Quick Sync）"
        self.version = "1.1.0"
        self._probe_cache = {}
    
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
                encoding='utf-8',
                errors='replace',
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
                encoding='utf-8',
                errors='replace',
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
    
    def _get_video_controllers(self):
        """获取系统中的显卡控制器名称（跨平台，尽力而为）"""
        controllers = []
        try:
            if os.name == 'nt':
                # Windows：使用 PowerShell 枚举显示适配器
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                     "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.splitlines():
                        name = line.strip()
                        if name:
                            controllers.append({"name": name})
            else:
                # Linux：使用 lspci
                result = subprocess.run(
                    ["lspci"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        lower = line.lower()
                        if any(k in lower for k in (
                            "vga compatible controller",
                            "3d controller",
                            "display controller",
                        )):
                            name = line.split(":", 2)[-1].strip()
                            if name:
                                controllers.append({"name": name})
        except Exception:
            pass
        return controllers
    
    def _get_hardware_gpu_info(self):
        """汇总各厂商显卡型号信息，形如 {'nvidia': {...}, 'intel': {...}}"""
        info = {}
        
        # NVIDIA 优先使用 nvidia-smi（可同时获得显存信息）
        nvidia = self._get_nvidia_gpu_info()
        if nvidia.get("model") and nvidia.get("model") != "未知":
            info["nvidia"] = {
                "model": nvidia.get("model"),
                "memory": nvidia.get("memory", "未知")
            }
        
        # 其余厂商从系统显卡列表推断
        for controller in self._get_video_controllers():
            name = controller.get("name", "")
            lower = name.lower()
            if "nvidia" in lower and "nvidia" not in info:
                info["nvidia"] = {"model": name, "memory": "未知"}
            elif "intel" in lower and "intel" not in info:
                info["intel"] = {"model": name}
            elif ("amd" in lower or "radeon" in lower) and "amd" not in info:
                info["amd"] = {"model": name}
        
        return info
    
    @staticmethod
    def _extract_ffmpeg_error(stderr):
        """从 ffmpeg stderr 中提取一行简洁的错误摘要"""
        if not stderr:
            return ""
        lines = [line.strip() for line in stderr.strip().splitlines() if line.strip()]
        if not lines:
            return ""
        # 优先返回包含错误关键字的那一行（ffmpeg 的详细错误通常在开头）
        keywords = (
            "error", "failed", "cannot", "no capable", "not supported",
            "unable", "invalid", "not found", "openencodesession", "no such",
            "no device", "device not",
        )
        for line in lines:
            lower = line.lower()
            if any(k in lower for k in keywords):
                return line[:200]
        return lines[0][:200]
    
    def _probe_encoder(self, encoder):
        """实际执行一次极短的编码，验证编码器在当前硬件上是否真的可用。
        
        仅检查 `ffmpeg -encoders` 是不够的：Windows/macOS 的 ffmpeg 通常默认
        编译了 NVENC/AMF 等编码器，但没有对应硬件时依然会列出，只有在真正
        编码时才会报错。
        """
        if encoder in self._probe_cache:
            return self._probe_cache[encoder]
        
        cfg = self._ENCODERS.get(encoder, {})
        # 纯 CPU 编码器无需探测
        if encoder == "libx264":
            result = {"available": True, "reason": ""}
            self._probe_cache[encoder] = result
            return result
        
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", "testsrc=size=320x240:rate=25",
            "-frames:v", "1",
            "-c:v", encoder,
        ]
        if cfg.get("pix_fmt"):
            cmd.extend(["-pix_fmt", cfg["pix_fmt"]])
        cmd.extend(["-f", "null", "-"])
        
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            if proc.returncode == 0:
                result = {"available": True, "reason": ""}
            else:
                result = {
                    "available": False,
                    "reason": self._extract_ffmpeg_error(proc.stderr) or "硬件不可用"
                }
        except subprocess.TimeoutExpired:
            result = {"available": False, "reason": "检测超时"}
        except FileNotFoundError:
            result = {"available": False, "reason": "未找到 ffmpeg"}
        except Exception as e:
            result = {"available": False, "reason": str(e)}
        
        self._probe_cache[encoder] = result
        return result
    
    def _select_auto_encoder(self, encoders=None):
        """按优先级选择第一个真正可用的编码器"""
        if encoders is None:
            check = self._check_gpu()
            encoders = check.get("encoders", {}) if check.get("success") else {}
        
        for key in self._AUTO_PRIORITY:
            entry = encoders.get(key)
            if entry and entry.get("available"):
                return entry.get("encoder")
        return "libx264"
    
    def _check_gpu(self):
        """检测可用的GPU编码器并获取显卡信息（通过真实编码探测硬件）"""
        if not self._check_ffmpeg():
            return {
                "success": False,
                "error": "未检测到ffmpeg，请先安装 ffmpeg"
            }
        
        try:
            # 获取ffmpeg支持的编码器列表（仅用于判断是否编译了该编码器）
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            
            encoders_output = result.stdout or ""
            
            # 获取各厂商显卡信息
            gpu_info = self._get_hardware_gpu_info()
            
            encoders = {}
            hardware_encoders = (
                ("nvidia", "h264_nvenc"),
                ("amd", "h264_amf"),
                ("intel", "h264_qsv"),
            )
            
            for key, encoder_id in hardware_encoders:
                cfg = self._ENCODERS[encoder_id]
                entry = {
                    "available": False,
                    "name": cfg["name"],
                    "encoder": encoder_id,
                    "vendor": key,
                    "reason": ""
                }
                
                if encoder_id in encoders_output:
                    # 编译了该编码器，进一步真实探测硬件是否可用
                    probe = self._probe_encoder(encoder_id)
                    entry["available"] = probe["available"]
                    if not probe["available"]:
                        entry["reason"] = probe.get("reason") or "硬件不可用"
                else:
                    entry["reason"] = "当前 ffmpeg 未编译该编码器"
                
                # 附加显卡型号信息
                vendor_info = gpu_info.get(key, {})
                entry["gpu_model"] = vendor_info.get("model", "未知")
                if key == "nvidia":
                    entry["gpu_memory"] = vendor_info.get("memory", "未知")
                
                # 未探测到对应硬件时，不展示型号信息
                if not entry["available"]:
                    entry["gpu_model"] = "未知"
                
                encoders[key] = entry
            
            cpu_available = "libx264" in encoders_output
            encoders["cpu"] = {
                "available": cpu_available,
                "name": self._ENCODERS["libx264"]["name"],
                "encoder": "libx264",
                "vendor": "cpu",
                "reason": "" if cpu_available else "当前 ffmpeg 未编译该编码器"
            }
            
            recommended = self._select_auto_encoder(encoders)
            
            return {
                "success": True,
                "ffmpeg_installed": True,
                "encoders": encoders,
                "recommended": recommended,
                "recommended_name": self._ENCODERS.get(recommended, {}).get("name", recommended)
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
                encoding='utf-8',
                errors='replace',
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
    
    def _resolve_encoder(self, encoder):
        """解析请求的编码器，返回 (编码器ID, 错误信息)"""
        if encoder in (None, "", "auto"):
            return self._select_auto_encoder(), None
        
        if encoder not in self._ENCODERS:
            return None, f"不支持的编码器: {encoder}"
        
        # 明确指定硬件编码器时，先确认真实可用，避免运行到一半才失败
        if encoder != "libx264":
            probe = self._probe_encoder(encoder)
            if not probe.get("available"):
                name = self._ENCODERS[encoder]["name"]
                reason = probe.get("reason") or "当前设备不支持"
                return None, (
                    f"{name} 在当前设备上不可用（{reason}）。"
                    f"请改用“自动选择”或 CPU (libx264)"
                )
        
        return encoder, None
    
    def _build_ffmpeg_cmd(self, encoder, params):
        """根据编码器构建 ffmpeg 命令"""
        cfg = self._ENCODERS.get(encoder, {})
        
        cmd = ["ffmpeg", "-hide_banner", "-i", params.get("input_file")]
        
        # 分辨率设置
        resolution = params.get("resolution", "original")
        if resolution and resolution != "original":
            cmd.extend(["-s", resolution])
        
        # 视频编码器
        cmd.extend(["-c:v", encoder])
        
        # 硬件编码器统一指定像素格式，提升兼容性
        if encoder != "libx264" and cfg.get("pix_fmt"):
            cmd.extend(["-pix_fmt", cfg["pix_fmt"]])
        
        # 码率设置
        bitrate = params.get("bitrate", "2M")
        if bitrate:
            cmd.extend(["-b:v", bitrate])
        
        # 预设设置（不同编码器的参数名和取值不同，例如 AMD 使用 -quality）
        preset = params.get("preset", "medium")
        preset_map = cfg.get("presets", {})
        mapped_preset = preset_map.get(preset) or preset_map.get("medium") or preset
        cmd.extend([cfg.get("preset_option", "-preset"), mapped_preset])
        
        # CPU 编码额外使用 CRF 控制质量
        if encoder == "libx264":
            crf = params.get("crf", 23)
            cmd.extend(["-crf", str(crf)])
        
        # 音频编码
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])
        
        # 输出文件（-y 覆盖已存在的文件）
        cmd.extend(["-y", params.get("output_file")])
        
        return cmd
    
    def _run_ffmpeg(self, cmd):
        """执行 ffmpeg 命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=3600  # 1小时超时
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stdout": "", "stderr": "压缩超时（超过1小时）"}
        except FileNotFoundError:
            return {"returncode": -1, "stdout": "", "stderr": "未找到 ffmpeg，请先安装 ffmpeg"}
        except Exception as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e)}
    
    def _compress_video(self, params):
        """压缩视频"""
        input_file = params.get("input_file")
        output_file = params.get("output_file")
        
        if not input_file or not output_file:
            return {"success": False, "error": "未指定输入或输出文件"}
        
        if not os.path.exists(input_file):
            return {"success": False, "error": f"输入文件不存在: {input_file}"}
        
        # 解析编码器（"auto" 会挑选真正可用的编码器）
        encoder, error = self._resolve_encoder(params.get("encoder", "auto"))
        if error:
            return {"success": False, "error": error}
        
        # 执行压缩
        result = self._run_ffmpeg(self._build_ffmpeg_cmd(encoder, params))
        
        # 硬件编码失败时自动回退到 CPU 编码，避免整个任务失败
        warning = None
        if result["returncode"] != 0 and encoder != "libx264":
            warning = (
                f"{self._ENCODERS[encoder]['name']} 编码失败"
                f"（{self._extract_ffmpeg_error(result.get('stderr')) or '未知原因'}），"
                f"已自动改用 CPU (libx264) 编码"
            )
            encoder = "libx264"
            result = self._run_ffmpeg(self._build_ffmpeg_cmd(encoder, params))
        
        if result["returncode"] != 0:
            return {"success": False, "error": f"压缩失败: {result['stderr']}"}
        
        if not os.path.exists(output_file):
            return {"success": False, "error": "输出文件未生成"}
        
        input_size = os.path.getsize(input_file)
        output_size = os.path.getsize(output_file)
        compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0
        
        payload = {
            "output_file": output_file,
            "input_size": input_size,
            "output_size": output_size,
            "compression_ratio": round(compression_ratio, 2),
            "encoder_used": encoder,
            "encoder_name": self._ENCODERS.get(encoder, {}).get("name", encoder)
        }
        if warning:
            payload["warning"] = warning
        
        return {
            "success": True,
            "message": "压缩完成",
            "result": payload
        }
