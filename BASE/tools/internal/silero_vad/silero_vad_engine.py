# BASE/tools/internal/silero_vad/silero_vad_engine.py
"""
Silero VAD Engine - High-performance voice activity detection
Optimized for real-time processing with GPU acceleration
"""
import torch
import torchaudio
import numpy as np
import sounddevice as sd
import queue
import threading
import time
from pathlib import Path
from typing import Optional, Callable, Tuple


class SileroVADEngine:
    """
    Self-contained Silero VAD engine for voice activity detection
    
    Features:
    - Real-time VAD with GPU acceleration
    - Configurable sensitivity
    - Speech segment extraction
    - Low latency processing
    """
    
    __slots__ = (
        'sample_rate', 'chunk_duration_ms', 'vad_threshold',
        'min_speech_duration_ms', 'min_silence_duration_ms', 'speech_pad_ms',
        'logger', '_device', '_vad_model', '_initialized', '_audio_queue',
        '_result_queue', '_is_listening', '_recognition_thread',
        '_audio_stream', '_speech_buffer', '_in_speech', '_speech_start_time',
        '_silence_start_time'
    )
    
    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration_ms: int = 500,
        vad_threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 500,
        speech_pad_ms: int = 200,
        logger=None
    ):
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.vad_threshold = vad_threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms
        self.logger = logger
        
        self._device = None
        self._vad_model = None
        self._initialized = False
        
        self._audio_queue = None
        self._result_queue = None
        self._is_listening = False
        self._recognition_thread = None
        self._audio_stream = None
        
        self._speech_buffer = []
        self._in_speech = False
        self._speech_start_time = 0
        self._silence_start_time = 0
    
    async def initialize(self) -> bool:
        """Initialize Silero VAD model"""
        try:
            if self.logger:
                self.logger.system("[Silero VAD] Initializing...")
            
            self._device = self._get_best_device()
            
            if self.logger:
                self.logger.system(f"[Silero VAD] Device: {self._device.upper()}")
            
            if self.logger:
                self.logger.system("[Silero VAD] Loading model...")
            
            success = self._load_vad_model()
            
            if not success:
                return False
            
            self._initialized = True
            
            if self.logger:
                self.logger.success("[Silero VAD] Ready")
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Silero VAD] Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def cleanup(self):
        """Cleanup Silero VAD resources"""
        self.stop_listening()
        
        if self._vad_model:
            del self._vad_model
            self._vad_model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        if self.logger:
            self.logger.system("[Silero VAD] Cleaned up")
    
    def start_listening(self, on_speech_callback: Optional[Callable] = None) -> bool:
        """Start listening for speech"""
        if not self._initialized:
            if self.logger:
                self.logger.error("[Silero VAD] Not initialized")
            return False
        
        if self._is_listening:
            if self.logger:
                self.logger.warning("[Silero VAD] Already listening")
            return True
        
        self._audio_queue = queue.Queue(maxsize=50)
        self._result_queue = queue.Queue(maxsize=20)
        
        self._is_listening = True
        
        self._recognition_thread = threading.Thread(
            target=lambda: self._vad_worker(on_speech_callback),
            daemon=True,
            name="SileroVAD_Worker"
        )
        self._recognition_thread.start()
        
        self._audio_stream = self._start_audio_stream()
        
        if self.logger:
            self.logger.success("[Silero VAD] Started listening")
        
        return True
    
    def stop_listening(self):
        """Stop listening"""
        if not self._is_listening:
            return
        
        self._is_listening = False
        
        if self._audio_stream:
            try:
                self._audio_stream.stop()
                self._audio_stream.close()
            except:
                pass
            self._audio_stream = None
        
        if self._audio_queue:
            try:
                self._audio_queue.put(b"__EXIT__")
            except:
                pass
        
        if self._recognition_thread and self._recognition_thread.is_alive():
            self._recognition_thread.join(timeout=2.0)
        
        if self.logger:
            self.logger.system("[Silero VAD] Stopped listening")
    
    def get_device(self) -> str:
        """Get device string"""
        return self._device if self._device else "unknown"
    
    def _get_best_device(self) -> str:
        """Detect best available device"""
        if not torch.cuda.is_available():
            return 'cpu'
        
        try:
            test_tensor = torch.zeros(1).cuda()
            result = test_tensor + 1
            del test_tensor, result
            torch.cuda.empty_cache()
            return 'cuda'
        except:
            return 'cpu'
    
    def _load_vad_model(self) -> bool:
        """Load Silero VAD model"""
        try:
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            model.to(self._device)
            model.eval()
            
            self._vad_model = model
            
            if self.logger:
                self.logger.system("[Silero VAD] Model loaded")
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Silero VAD] Model load failed: {e}")
            return False
    
    def _vad_worker(self, on_speech_callback: Optional[Callable]):
        """Worker thread for VAD processing"""
        if self.logger:
            self.logger.system("[Silero VAD Worker] Started")
        
        # Silero VAD requires exactly 512 samples per chunk for 16kHz
        VAD_CHUNK_SIZE = 512
        accumulated_audio = []
        
        while self._is_listening:
            try:
                audio_chunk = self._audio_queue.get(timeout=0.5)
                
                if isinstance(audio_chunk, bytes) and audio_chunk == b"__EXIT__":
                    break
                
                accumulated_audio.append(audio_chunk)
                total_samples = sum(len(chunk) for chunk in accumulated_audio)
                
                # Process in fixed 512-sample chunks
                while total_samples >= VAD_CHUNK_SIZE:
                    # Concatenate accumulated audio
                    full_audio = np.concatenate(accumulated_audio)
                    
                    # Extract exactly 512 samples
                    audio_data = full_audio[:VAD_CHUNK_SIZE]
                    
                    # Keep remaining samples
                    remaining = full_audio[VAD_CHUNK_SIZE:]
                    accumulated_audio = [remaining] if len(remaining) > 0 else []
                    total_samples = len(remaining)
                    
                    speech_prob = self._process_chunk(audio_data)
                    
                    current_time = time.time()
                    
                    if speech_prob > self.vad_threshold:
                        if not self._in_speech:
                            self._in_speech = True
                            self._speech_start_time = current_time
                            self._speech_buffer = []
                        
                        self._speech_buffer.append(audio_data)
                        self._silence_start_time = 0
                    
                    else:
                        if self._in_speech:
                            if self._silence_start_time == 0:
                                self._silence_start_time = current_time
                            
                            silence_duration = (current_time - self._silence_start_time) * 1000
                            
                            if silence_duration >= self.min_silence_duration_ms:
                                speech_duration = (current_time - self._speech_start_time) * 1000
                                
                                if speech_duration >= self.min_speech_duration_ms:
                                    speech_audio = np.concatenate(self._speech_buffer)
                                    
                                    if on_speech_callback:
                                        try:
                                            on_speech_callback(speech_audio, self.sample_rate)
                                        except Exception as e:
                                            if self.logger:
                                                self.logger.error(f"[Silero VAD] Callback error: {e}")
                                
                                self._in_speech = False
                                self._speech_buffer = []
                                self._silence_start_time = 0
            
            except queue.Empty:
                continue
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[Silero VAD Worker] Error: {e}")
                import traceback
                traceback.print_exc()
        
        if self.logger:
            self.logger.system("[Silero VAD Worker] Stopped")
    
    def _process_chunk(self, audio_chunk: np.ndarray) -> float:
        """Process audio chunk and return speech probability"""
        try:
            audio_tensor = torch.from_numpy(audio_chunk).to(self._device)
            
            with torch.no_grad():
                speech_prob = self._vad_model(audio_tensor, self.sample_rate).item()
            
            return speech_prob
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Silero VAD] Chunk processing error: {e}")
            return 0.0
    
    def _start_audio_stream(self):
        """Start audio input stream"""
        PREFERRED_DEVICES = [1, 12, 29, 35]
        audio_device = None
        
        if self.logger:
            self.logger.system("[Silero VAD] Testing audio devices...")
        
        for device_idx in PREFERRED_DEVICES:
            try:
                device_info = sd.query_devices(device_idx)
                device_name = device_info['name']
                
                if 'cable' in device_name.lower() or 'vb-audio' in device_name.lower():
                    continue
                
                test_stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    blocksize=2048,
                    dtype=np.float32,
                    channels=1,
                    device=device_idx
                )
                test_stream.close()
                
                audio_device = device_idx
                if self.logger:
                    self.logger.system(f"[Silero VAD] Using device {audio_device}: {device_name}")
                break
                
            except Exception as e:
                continue
        
        if audio_device is None:
            if self.logger:
                self.logger.error("[Silero VAD] No working microphone found")
            raise RuntimeError("No functional audio input device available")
        
        # Use blocksize that's a multiple of 512 (Silero VAD requirement)
        # 512 samples = 32ms at 16kHz (very low latency)
        blocksize = 512
        
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=blocksize,
            device=audio_device,
            callback=self._audio_callback,
            latency='low'  # Low latency for real-time response
        )
        
        stream.start()
        
        if self.logger:
            self.logger.system("[Silero VAD] Audio stream active")
        
        return stream
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Audio input callback"""
        if status:
            if self.logger:
                self.logger.warning(f"[Silero VAD Audio] Status: {status}")
        
        audio_chunk = indata[:, 0].copy() if indata.ndim == 2 else indata.copy()
        
        try:
            self._audio_queue.put_nowait(audio_chunk)
        except queue.Full:
            pass