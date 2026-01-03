"""
Shared Voice Service - Single Vosk Instance for Multiple Agents
Location: BASE/tools/internal/voice/shared_voice_service.py

This service runs ONE Vosk instance and broadcasts recognized text to multiple
agent instances via observer pattern. Each agent subscribes to receive voice input.

Architecture:
- Single audio stream (one microphone)
- Single Vosk/Whisper model instance
- Multiple agent subscribers
- Thread-safe broadcasting
"""
import threading
import queue
import time
from typing import Callable, Dict, Set, Optional
from pathlib import Path


class VoiceServiceSubscriber:
    """Represents a single agent subscribed to voice input"""
    
    __slots__ = ('agent_id', 'callback', 'text_queue', 'filter_func', 'enabled')
    
    def __init__(self, agent_id: str, callback: Optional[Callable[[str], None]] = None):
        """
        Initialize subscriber
        
        Args:
            agent_id: Unique identifier for this agent
            callback: Optional callback function(text) for immediate notifications
        """
        self.agent_id = agent_id
        self.callback = callback
        self.text_queue = queue.Queue(maxsize=20)
        self.filter_func = None
        self.enabled = True
    
    def set_filter(self, filter_func: Callable[[str], bool]):
        """Set custom filter function for this subscriber"""
        self.filter_func = filter_func
    
    def should_receive(self, text: str) -> bool:
        """Check if subscriber should receive this text"""
        if not self.enabled:
            return False
        if self.filter_func:
            return self.filter_func(text)
        return True
    
    def deliver(self, text: str):
        """Deliver text to subscriber"""
        try:
            self.text_queue.put_nowait(text)
            if self.callback:
                self.callback(text)
        except queue.Full:
            try:
                self.text_queue.get_nowait()
                self.text_queue.put_nowait(text)
            except:
                pass


class SharedVoiceService:
    """
    Singleton voice service that manages one Vosk instance for multiple agents
    
    Usage:
        # In your main application startup:
        voice_service = SharedVoiceService.get_instance()
        voice_service.start()
        
        # In each agent's VoiceManager:
        service = SharedVoiceService.get_instance()
        subscriber_id = service.subscribe(agent_id="agent1", callback=self.on_voice_input)
        
        # When agent shuts down:
        service.unsubscribe(subscriber_id)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    __slots__ = ('_subscribers', '_subscribers_lock', '_running', '_audio_thread',
                 '_recognition_thread', '_stream', '_raw_queue', '_recognition_backend',
                 '_recognition_device', '_whisper_model', '_vosk_model', '_init_error',
                 'logger')
    
    def __init__(self):
        """Private constructor - use get_instance() instead"""
        if SharedVoiceService._instance is not None:
            raise RuntimeError("Use SharedVoiceService.get_instance()")
        
        self._subscribers: Dict[str, VoiceServiceSubscriber] = {}
        self._subscribers_lock = threading.Lock()
        self._running = False
        self._audio_thread = None
        self._recognition_thread = None
        
        self._stream = None
        self._raw_queue = None
        self._recognition_backend = None
        self._recognition_device = None
        self._whisper_model = None
        self._vosk_model = None
        self._init_error = None
        
        self.logger = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance (thread-safe)"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def set_logger(self, logger):
        """Set logger for service (optional)"""
        self.logger = logger
    
    def _log(self, message: str, level: str = "info"):
        """Internal logging helper"""
        prefix = "[SharedVoice]"
        if self.logger:
            if level == "error":
                self.logger.error(f"{prefix} {message}")
            elif level == "success":
                self.logger.success(f"{prefix} {message}")
            else:
                self.logger.system(f"{prefix} {message}")
        else:
            print(f"{prefix} {message}")
    
    def subscribe(self, agent_id: str, callback: Optional[Callable[[str], None]] = None,
                  filter_func: Optional[Callable[[str], bool]] = None) -> str:
        """
        Subscribe an agent to receive voice input
        
        Args:
            agent_id: Unique identifier for the agent
            callback: Optional callback function(text) for immediate delivery
            filter_func: Optional filter function(text) -> bool to filter messages
            
        Returns:
            Subscriber ID (same as agent_id)
        """
        with self._subscribers_lock:
            if agent_id in self._subscribers:
                self._log(f"Agent '{agent_id}' already subscribed", "error")
                return agent_id
            
            subscriber = VoiceServiceSubscriber(agent_id, callback)
            if filter_func:
                subscriber.set_filter(filter_func)
            
            self._subscribers[agent_id] = subscriber
            self._log(f"Agent '{agent_id}' subscribed (total: {len(self._subscribers)})", "success")
            
            return agent_id
    
    def unsubscribe(self, agent_id: str):
        """Unsubscribe an agent from voice input"""
        with self._subscribers_lock:
            if agent_id in self._subscribers:
                del self._subscribers[agent_id]
                self._log(f"Agent '{agent_id}' unsubscribed (remaining: {len(self._subscribers)})")
            else:
                self._log(f"Agent '{agent_id}' not found in subscribers", "error")
    
    def enable_subscriber(self, agent_id: str, enabled: bool = True):
        """Enable or disable a subscriber without removing it"""
        with self._subscribers_lock:
            if agent_id in self._subscribers:
                self._subscribers[agent_id].enabled = enabled
                status = "enabled" if enabled else "disabled"
                self._log(f"Agent '{agent_id}' {status}")
            else:
                self._log(f"Agent '{agent_id}' not found", "error")
    
    def get_subscriber_queue(self, agent_id: str) -> Optional[queue.Queue]:
        """Get the text queue for a specific subscriber"""
        with self._subscribers_lock:
            if agent_id in self._subscribers:
                return self._subscribers[agent_id].text_queue
            return None
    
    def _broadcast_text(self, text: str):
        """Broadcast recognized text to all active subscribers"""
        with self._subscribers_lock:
            delivered_to = []
            for subscriber in self._subscribers.values():
                if subscriber.should_receive(text):
                    subscriber.deliver(text)
                    delivered_to.append(subscriber.agent_id)
            
            if delivered_to:
                agents_str = ", ".join(delivered_to)
                self._log(f"Broadcast to: {agents_str}")
    
    def start(self, preferred_backend: str = "auto", device_indices: Optional[list] = None):
        """
        Start shared voice service
        
        Args:
            preferred_backend: "whisper", "vosk", or "auto" (try GPU first)
            device_indices: Optional list of preferred audio device indices
        """
        if self._running:
            self._log("Service already running", "error")
            return False
        
        try:
            self._log("Starting shared voice service...")
            
            from BASE.tools.internal.voice.voice_to_text import (
                samplerate, AUDIO_BLOCKSIZE, QUEUE_MAX_SIZE
            )
            
            self._raw_queue = queue.Queue(maxsize=QUEUE_MAX_SIZE)
            
            if preferred_backend == "auto" or preferred_backend == "whisper":
                if self._init_whisper():
                    self._log("Using Whisper (GPU)", "success")
                elif preferred_backend != "whisper":
                    if self._init_vosk():
                        self._log("Using Vosk (CPU)", "success")
                    else:
                        raise RuntimeError("Failed to initialize any recognition backend")
                else:
                    raise RuntimeError("Whisper initialization failed")
            else:
                if not self._init_vosk():
                    raise RuntimeError("Vosk initialization failed")
                self._log("Using Vosk (CPU)", "success")
            
            if not self._start_audio_stream(device_indices):
                raise RuntimeError("Failed to start audio stream")
            
            self._start_recognition_worker()
            
            self._running = True
            self._log("Shared voice service started successfully", "success")
            return True
            
        except Exception as e:
            self._log(f"Failed to start service: {e}", "error")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_whisper(self) -> bool:
        """Initialize Whisper GPU backend"""
        try:
            from BASE.tools.internal.voice.voice_to_text import load_whisper_model
            self._whisper_model = load_whisper_model()
            self._recognition_backend = "whisper"
            self._recognition_device = "cuda"
            return True
        except Exception as e:
            self._log(f"Whisper init failed: {e}", "error")
            return False
    
    def _init_vosk(self) -> bool:
        """Initialize Vosk CPU backend"""
        try:
            from BASE.tools.internal.voice.voice_to_text import load_vosk_model
            self._vosk_model = load_vosk_model()
            self._recognition_backend = "vosk"
            self._recognition_device = "cpu"
            return True
        except Exception as e:
            self._log(f"Vosk init failed: {e}", "error")
            return False
    
    def _start_audio_stream(self, device_indices: Optional[list] = None) -> bool:
        """Start audio capture stream"""
        import sounddevice as sd
        import numpy as np
        from BASE.tools.internal.voice.voice_to_text import (
            samplerate, AUDIO_BLOCKSIZE
        )
        
        if device_indices is None:
            device_indices = [1, 12, 29, 35]
        
        audio_device = None
        
        for device_idx in device_indices:
            try:
                device_info = sd.query_devices(device_idx)
                device_name = device_info['name']
                
                if 'cable' in device_name.lower() or 'vb-audio' in device_name.lower():
                    continue
                
                test_stream = sd.RawInputStream(
                    samplerate=samplerate,
                    blocksize=2048,
                    dtype="int16",
                    channels=1,
                    device=device_idx
                )
                test_stream.close()
                
                audio_device = device_idx
                self._log(f"Audio device: [{audio_device}] {device_name}", "success")
                break
                
            except Exception as e:
                continue
        
        if audio_device is None:
            self._log("No working microphone found", "error")
            return False
        
        def audio_callback(indata, frames, time_info, status):
            try:
                self._raw_queue.put_nowait(bytes(indata))
            except queue.Full:
                pass
        
        self._stream = sd.RawInputStream(
            samplerate=samplerate,
            blocksize=AUDIO_BLOCKSIZE,
            dtype="int16",
            channels=1,
            device=audio_device,
            callback=audio_callback,
            latency='high'
        )
        self._stream.start()
        
        return True
    
    def _start_recognition_worker(self):
        """Start recognition worker thread"""
        if self._recognition_backend == "whisper":
            self._recognition_thread = threading.Thread(
                target=self._whisper_worker,
                daemon=True,
                name="SharedVoice-Whisper"
            )
        else:
            self._recognition_thread = threading.Thread(
                target=self._vosk_worker,
                daemon=True,
                name="SharedVoice-Vosk"
            )
        
        self._recognition_thread.start()
    
    def _whisper_worker(self):
        """Whisper recognition worker"""
        import numpy as np
        from BASE.tools.internal.voice.voice_to_text import (
            samplerate, AUDIO_CHUNK_DURATION, GPU_CONFIG
        )
        
        try:
            from personality.bot_info import agentname
        except:
            agentname = "Anna"
        
        audio_buffer = []
        samples_per_chunk = int(samplerate * AUDIO_CHUNK_DURATION)
        
        while self._running:
            try:
                data = self._raw_queue.get(timeout=0.5)
                
                if data == b"__EXIT__":
                    break
                
                audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                audio_buffer.extend(audio_data)
                
                if len(audio_buffer) >= samples_per_chunk:
                    audio_chunk = np.array(audio_buffer[:samples_per_chunk], dtype=np.float32)
                    audio_buffer = audio_buffer[samples_per_chunk:]
                    
                    segments, info = self._whisper_model.transcribe(
                        audio_chunk,
                        language="en",
                        beam_size=GPU_CONFIG['beam_size'],
                        vad_filter=True,
                        vad_parameters=dict(
                            threshold=0.5,
                            min_speech_duration_ms=250,
                            min_silence_duration_ms=500
                        ),
                        without_timestamps=True,
                    )
                    
                    text = " ".join([s.text.strip() for s in segments])
                    
                    if len(text) >= 5 and agentname.lower() not in text.lower():
                        self._broadcast_text(text)
                        
            except queue.Empty:
                continue
            except Exception as e:
                self._log(f"Whisper worker error: {e}", "error")
                if "cudnn" in str(e).lower():
                    break
    
    def _vosk_worker(self):
        """Vosk recognition worker"""
        from vosk import KaldiRecognizer
        import json
        from BASE.tools.internal.voice.voice_to_text import samplerate
        
        try:
            from personality.bot_info import agentname
        except:
            agentname = "Anna"
        
        rec = KaldiRecognizer(self._vosk_model, samplerate)
        
        while self._running:
            try:
                data = self._raw_queue.get(timeout=0.5)
                
                if data == b"__EXIT__":
                    break
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    
                    if len(text) >= 5 and agentname.lower() not in text.lower():
                        self._broadcast_text(text)
                        
            except queue.Empty:
                continue
            except Exception as e:
                self._log(f"Vosk worker error: {e}", "error")
    
    def stop(self):
        """Stop shared voice service"""
        if not self._running:
            return
        
        self._log("Stopping shared voice service...")
        self._running = False
        
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except:
                pass
            self._stream = None
        
        if self._raw_queue:
            try:
                self._raw_queue.put(b"__EXIT__")
            except:
                pass
        
        if self._recognition_thread and self._recognition_thread.is_alive():
            self._recognition_thread.join(timeout=2.0)
        
        self._log("Shared voice service stopped", "success")
    
    def get_status(self) -> Dict:
        """Get service status"""
        with self._subscribers_lock:
            return {
                'running': self._running,
                'backend': self._recognition_backend,
                'device': self._recognition_device,
                'subscribers': len(self._subscribers),
                'subscriber_ids': list(self._subscribers.keys())
            }