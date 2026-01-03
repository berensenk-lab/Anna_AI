# ============================================================================
# Filename: BASE/tools/internal/voice/tts_tool.py
# ============================================================================
"""
Unified TTS Tool - Backend-agnostic orchestrator for text-to-speech

This tool manages TTS operations regardless of which backend is used.
It handles threading, interruption, and provides a consistent interface
to the rest of the system.

The backend (XTTS, pyttsx3, etc.) is injected during initialization.
"""
import threading
from typing import Optional, Dict, Iterator
from BASE.handlers.tts_interface import TTSInterface
from BASE.core.logger import Logger


class TTSTool:
    """
    Unified TTS orchestrator with swappable backends
    
    Responsibilities:
    - Manage speech state (is_speaking)
    - Handle thread safety (locks)
    - Coordinate interruptions (stop_event)
    - Provide consistent logging
    - Delegate actual speech to backend
    
    Does NOT:
    - Know about backend implementation details
    - Handle audio generation directly
    - Manage device selection
    """

    __slots__ = ('backend', 'logger', '_is_speaking', '_speech_lock', '_stop_event')
    
    def __init__(self, backend: TTSInterface, logger: Optional[Logger] = None):
        """
        Initialize TTS tool with a backend
        
        Args:
            backend: TTS backend implementing TTSInterface
            logger: Optional logger for output (creates default if None)
        """
        self.backend = backend
        self.logger = logger or Logger(name="TTSTool")
        
        # Thread safety
        self._is_speaking = False
        self._speech_lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Log initialization
        if self.backend.is_available():
            info = self.backend.get_voice_info()
            self.logger.speech(f"TTS initialized: {info.get('name', 'Unknown')} ({info.get('type', 'Unknown')})")
        else:
            self.logger.warning("TTS backend initialized but not available")
    
    def is_available(self) -> bool:
        """
        Check if TTS is ready to use
        
        Returns:
            bool: True if backend is available
        """
        return self.backend.is_available()
    
    def speak(self, text: str, stream: bool = True) -> str:
        """
        Speak text using the configured backend
        
        This method handles:
        - Input validation
        - Stopping previous speech
        - Thread-safe state management
        - Error handling and logging
        - Passing control to backend
        
        Args:
            text: Text to speak
            stream: Whether to stream audio (if backend supports it)
            
        Returns:
            str: "Speech completed", "Interrupted", or error message
        """
        # Validate input
        if not text or not text.strip():
            self.logger.warning("Attempted to speak empty text")
            return "No text to speak"
        
        if not self.is_available():
            self.logger.error("TTS not available")
            return "TTS not available"
        
        # Stop any current speech
        with self._speech_lock:
            if self._is_speaking:
                self.logger.speech("Stopping previous speech for new text")
                self._stop_event.set()
                # Brief wait for stop to take effect
                import time
                time.sleep(0.1)
            
            # Mark as speaking and reset stop event
            self._is_speaking = True
            self._stop_event.clear()
        
        # Delegate to backend
        try:
            self.logger.speech(f"Speaking: {text}{'...' if len(text) > 50 else ''}")
            
            # Backend receives stop_event to respect interruptions
            result = self.backend.speak(text, stream, stop_event=self._stop_event)
            
            # Log result
            if "completed" in result.lower():
                self.logger.speech("[SUCCESS] Speech completed")
            elif "interrupted" in result.lower():
                self.logger.speech("[WARNING] Speech interrupted")
            elif "error" in result.lower():
                self.logger.error(f"TTS error: {result}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"TTS exception: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"
        
        finally:
            # Always release lock and reset state
            with self._speech_lock:
                self._is_speaking = False
                self._stop_event.clear()
    
    def stop(self):
        """
        Stop any currently playing speech
        
        Thread-safe and safe to call even if nothing is playing
        """
        with self._speech_lock:
            if self._is_speaking:
                self.logger.speech("Stopping speech")
                self._stop_event.set()
                self.backend.stop()
                self._is_speaking = False
            else:
                self.logger.speech("Stop called but nothing playing")
    
    def get_voice_info(self) -> Dict:
        """
        Get information about current voice configuration
        
        Returns:
            Dict with voice details from backend
        """
        return self.backend.get_voice_info()
    
    def get_status(self) -> Dict:
        """
        Get current TTS status
        
        Returns:
            Dict with status information
        """
        return {
            'available': self.is_available(),
            'speaking': self._is_speaking,
            'backend': self.backend.get_voice_info().get('type', 'Unknown')
        }
    
class TTSToolStreamingMethods:
    """
    New streaming methods to ADD to TTSTool class
    """
    
    def speak_chunks(self, text_chunks: Iterator[str]) -> str:
        """
        Speak text chunks as they arrive (streaming mode)
        
        NEW METHOD - Add to TTSTool
        
        This is the main interface for streaming text chunks to TTS.
        It handles thread safety and delegates to the backend.
        
        Args:
            text_chunks: Iterator yielding text chunks
            
        Returns:
            "Speech completed", "Interrupted", or error message
        """
        if not self.is_available():
            self.logger.error("TTS not available")
            return "TTS not available"
        
        # Stop any current speech
        with self._speech_lock:
            if self._is_speaking:
                self.logger.speech("Stopping previous speech for new stream")
                self._stop_event.set()
                time.sleep(0.1)
            
            # Mark as speaking and reset stop event
            self._is_speaking = True
            self._stop_event.clear()
        
        try:
            self.logger.speech("Starting streaming speech")
            
            # Check if backend supports chunk streaming
            if hasattr(self.backend, 'speak_streaming_chunks'):
                result = self.backend.speak_streaming_chunks(
                    text_chunks=text_chunks,
                    stop_event=self._stop_event
                )
            else:
                # Fallback: accumulate chunks and speak normally
                self.logger.warning("Backend doesn't support streaming - using fallback")
                accumulated_text = " ".join(text_chunks)
                result = self.backend.speak(accumulated_text, stream=True, stop_event=self._stop_event)
            
            # Log result
            if "completed" in result.lower():
                self.logger.speech("[SUCCESS] Streaming speech completed")
            elif "interrupted" in result.lower():
                self.logger.speech("[WARNING] Streaming speech interrupted")
            elif "error" in result.lower():
                self.logger.error(f"Streaming TTS error: {result}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Streaming TTS exception: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"
        
        finally:
            # Always release lock and reset state
            with self._speech_lock:
                self._is_speaking = False
                self._stop_event.clear()

class ChunkBuffer:
    """
    Utility class for buffering text chunks until speakable unit
    
    Use this to accumulate streaming text chunks until we have
    a natural break point (punctuation, minimum word count).
    """

    __slots__ = ('min_words', 'max_words', 'buffer')
    
    def __init__(self, min_words: int = 3, max_words: int = 10):
        """
        Initialize chunk buffer
        
        Args:
            min_words: Minimum words before emitting chunk
            max_words: Maximum words before forcing emit
        """
        self.min_words = min_words
        self.max_words = max_words
        self.buffer = ""
    
    def add_text(self, text: str) -> Optional[str]:
        """
        Add text to buffer, return chunk if ready
        
        Args:
            text: Text to add to buffer
            
        Returns:
            Speakable chunk if ready, None if still buffering
        """
        self.buffer += text
        
        # Check for natural break points
        has_punctuation = any(char in self.buffer for char in '.!?,;:')
        word_count = len(self.buffer.split())
        
        # Emit if:
        # 1. Has punctuation AND meets minimum words
        # 2. Exceeds maximum words (force emit)
        if (has_punctuation and word_count >= self.min_words) or word_count >= self.max_words:
            chunk = self.buffer.strip()
            self.buffer = ""
            return chunk
        
        return None
    
    def flush(self) -> Optional[str]:
        """
        Flush remaining buffer content
        
        Returns:
            Buffered text if any, None otherwise
        """
        if self.buffer.strip():
            chunk = self.buffer.strip()
            self.buffer = ""
            return chunk
        return None