# BASE/tools/internal/silero_vad/tool.py
"""
Silero VAD Internal Tool - Real-time Voice Activity Detection
GPU-accelerated VAD with speech recognition integration
"""
from typing import Optional
import threading
import queue
from pathlib import Path
import numpy as np

from BASE.handlers.internal_tool_interface import InternalToolInterface


class SileroVADTool(InternalToolInterface):
    """
    Real-time voice activity detection using Silero VAD
    
    Features:
    - GPU-accelerated VAD
    - Real-time speech detection
    - Configurable sensitivity
    - Voice Hub integration
    - Speech recognition integration
    """
    
    __slots__ = (
        '_config', '_controls', '_logger', '_is_available',
        '_vad_engine', '_voice_enabled', '_speech_recognizer',
        '_text_queue', 'hub_client', 'on_speech_callback', '_recognizer_type'
    )
    
    @property
    def tool_name(self) -> str:
        return "silero_vad"
    
    @property
    def service_type(self) -> str:
        return "voice_input"
    
    def __init__(self, config, controls, logger=None):
        self._config = config
        self._controls = controls
        self._logger = logger
        
        self._is_available = False
        self._vad_engine = None
        self._voice_enabled = False
        self._speech_recognizer = None
        self._text_queue = None
        self._recognizer_type = None  # 'whisper' or 'vosk'
        
        self.hub_client = None
        self.on_speech_callback = None
    
    async def initialize(self) -> bool:
        """Initialize Silero VAD engine"""
        if self._logger:
            self._logger.system("[Silero VAD] Loading VAD model...")
        
        try:
            from BASE.tools.internal.silero_vad.silero_vad_engine import SileroVADEngine
            
            self._vad_engine = SileroVADEngine(
                sample_rate=16000,
                chunk_duration_ms=500,
                vad_threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=500,
                speech_pad_ms=200,
                logger=self._logger
            )
            
            success = await self._vad_engine.initialize()
            
            if success:
                success = self._init_speech_recognizer()
                
                if success:
                    self._is_available = True
                    
                    if self._logger:
                        device = self._vad_engine.get_device()
                        self._logger.success(f"[Silero VAD] Ready on {device.upper()}")
                    
                    return True
                else:
                    if self._logger:
                        self._logger.error("[Silero VAD] Speech recognizer init failed")
                    return False
            else:
                if self._logger:
                    self._logger.error("[Silero VAD] Engine initialization failed")
                return False
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_speech_recognizer(self) -> bool:
        """Initialize speech recognizer for transcription"""
        try:
            import torch
            
            if not torch.cuda.is_available():
                if self._logger:
                    self._logger.warning("[Silero VAD] CUDA not available, using CPU recognizer")
                return self._init_vosk_recognizer()
            
            return self._init_whisper_recognizer()
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Recognizer init error: {e}")
            return False
    
    def _init_whisper_recognizer(self) -> bool:
        """Initialize Whisper for GPU-based transcription"""
        try:
            # Setup CUDA paths before importing
            self._setup_cuda_paths()
            
            from faster_whisper import WhisperModel
            import torch
            
            # Try CUDA first, fall back to CPU if unavailable
            if torch.cuda.is_available():
                try:
                    self._speech_recognizer = WhisperModel(
                        'small',
                        device='cuda',
                        compute_type='int8'
                    )
                    
                    if self._logger:
                        self._logger.system("[Silero VAD] Using Faster-Whisper (GPU) for transcription")
                except Exception as cuda_error:
                    if self._logger:
                        self._logger.warning(f"[Silero VAD] CUDA Whisper failed: {cuda_error}")
                        self._logger.system("[Silero VAD] Trying Whisper on CPU...")
                    
                    self._speech_recognizer = WhisperModel(
                        'small',
                        device='cpu',
                        compute_type='int8'
                    )
                    
                    if self._logger:
                        self._logger.system("[Silero VAD] Using Faster-Whisper (CPU) for transcription")
            else:
                # No CUDA available, use CPU
                self._speech_recognizer = WhisperModel(
                    'small',
                    device='cpu',
                    compute_type='int8'
                )
                
                if self._logger:
                    self._logger.system("[Silero VAD] Using Faster-Whisper (CPU) for transcription")
            
            self._recognizer_type = 'whisper'
            return True
        
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[Silero VAD] Whisper init failed: {e}")
                self._logger.system("[Silero VAD] Falling back to Vosk")
            return self._init_vosk_recognizer()
    
    def _setup_cuda_paths(self):
        """Add CUDA libraries to system PATH"""
        try:
            import sys
            import os
            from pathlib import Path
            
            site_packages = None
            for path in sys.path:
                if 'site-packages' in path and os.path.exists(path):
                    site_packages = Path(path)
                    break
            
            if site_packages:
                nvidia_dirs = [
                    site_packages / "nvidia" / "cublas" / "bin",
                    site_packages / "nvidia" / "cudnn" / "bin",
                    site_packages / "nvidia" / "cuda_runtime" / "bin",
                ]
                
                for cuda_dir in nvidia_dirs:
                    if cuda_dir.exists():
                        cuda_dir_str = str(cuda_dir)
                        if cuda_dir_str not in os.environ.get('PATH', ''):
                            os.environ['PATH'] = cuda_dir_str + os.pathsep + os.environ.get('PATH', '')
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[Silero VAD] CUDA path setup failed: {e}")
    
    def _init_vosk_recognizer(self) -> bool:
        """Initialize Vosk for CPU-based transcription"""
        try:
            from vosk import Model, KaldiRecognizer
            
            project_root = Path(__file__).parent.parent.parent.parent.parent
            model_path = project_root / "models" / "vosk-model-en-us-0.42-gigaspeech"
            
            if not model_path.exists():
                if self._logger:
                    self._logger.error(f"[Silero VAD] Vosk model not found: {model_path}")
                return False
            
            vosk_model = Model(str(model_path))
            self._speech_recognizer = KaldiRecognizer(vosk_model, 16000)
            self._speech_recognizer.SetWords(True)
            
            self._recognizer_type = 'vosk'
            
            if self._logger:
                self._logger.system("[Silero VAD] Using Vosk for transcription")
            
            return True
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Vosk init failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup Silero VAD resources"""
        self.stop_listening()
        
        if self._vad_engine:
            await self._vad_engine.cleanup()
        
        if self._speech_recognizer:
            del self._speech_recognizer
            self._speech_recognizer = None
        
        if self._logger:
            self._logger.system("[Silero VAD] Cleaned up")
    
    def is_available(self) -> bool:
        """Check if Silero VAD is ready"""
        return self._is_available
    
    def start_listening(self, callback=None) -> bool:
        """Start voice recognition"""
        if not self.is_available():
            return False
        
        if self._voice_enabled:
            if self._logger:
                self._logger.warning("[Silero VAD] Already listening")
            return True
        
        self.on_speech_callback = callback
        
        self._text_queue = queue.Queue(maxsize=20)
        
        success = self._vad_engine.start_listening(
            on_speech_callback=self._on_speech_detected
        )
        
        if not success:
            return False
        
        self._voice_enabled = True
        
        if self._logger:
            self._logger.success("[Silero VAD] Started listening")
        
        processing_thread = threading.Thread(
            target=self._speech_processing_loop,
            daemon=True
        )
        processing_thread.start()
        
        return True
    
    def stop_listening(self):
        """Stop voice recognition"""
        if not self._voice_enabled:
            return
        
        self._voice_enabled = False
        
        if self._vad_engine:
            self._vad_engine.stop_listening()
        
        if self._logger:
            self._logger.system("[Silero VAD] Stopped listening")
    
    def _on_speech_detected(self, audio_data: np.ndarray, sample_rate: int):
        """Callback when speech is detected by VAD"""
        if not self._voice_enabled:
            return
        
        try:
            text = self._transcribe_audio(audio_data, sample_rate)
            
            if text and len(text) >= 3:
                try:
                    self._text_queue.put_nowait(text)
                except queue.Full:
                    try:
                        self._text_queue.get_nowait()
                        self._text_queue.put_nowait(text)
                    except:
                        pass
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Transcription error: {e}")
    
    def _transcribe_audio(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe audio using speech recognizer"""
        try:
            if self._recognizer_type == 'whisper':
                return self._transcribe_whisper(audio_data, sample_rate)
            elif self._recognizer_type == 'vosk':
                return self._transcribe_vosk(audio_data, sample_rate)
            else:
                if self._logger:
                    self._logger.error(f"[Silero VAD] Unknown recognizer type: {self._recognizer_type}")
                return ""
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Transcription failed: {e}")
            return ""
    
    def _transcribe_whisper(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe using Faster-Whisper"""
        try:
            segments, info = self._speech_recognizer.transcribe(
                audio_data,
                language='en',
                beam_size=5,
                vad_filter=False
            )
            
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            
            return ' '.join(text_parts)
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Whisper transcription error: {e}")
            return ""
    
    def _transcribe_vosk(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe using Vosk"""
        try:
            import json
            
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            if self._speech_recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self._speech_recognizer.Result())
                return result.get("text", "").strip()
            
            return ""
        
        except Exception as e:
            if self._logger:
                self._logger.error(f"[Silero VAD] Vosk transcription error: {e}")
            return ""
    
    def _speech_processing_loop(self):
        """Process recognized text from queue"""
        from personality.bot_info import agentname, username
        
        while self._voice_enabled:
            try:
                text = self._text_queue.get(timeout=0.1)
                
                if text and len(text) >= 3:
                    if agentname.lower() not in text.lower():
                        if self._logger:
                            self._logger.speech(f"[User] {text}")
                        
                        if self.on_speech_callback:
                            self.on_speech_callback(username, text)
            
            except queue.Empty:
                continue
            except Exception as e:
                if self._logger:
                    self._logger.error(f"[Silero VAD] Processing error: {e}")
    
    def set_hub_client(self, hub_client):
        """Inject Voice Hub client"""
        self.hub_client = hub_client