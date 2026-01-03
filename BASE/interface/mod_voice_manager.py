"""
Modified Voice Manager - Connects to Shared Voice Service
Location: BASE/interface/voice_manager.py

MODIFIED: Instead of initializing its own Vosk/Whisper instance, this manager
subscribes to the SharedVoiceService singleton, allowing multiple agents to
share a single voice recognition instance.

AUTOMATIC AGENT ID: Uses agent name from Config class (personality/bot_info.py)
No manual agent_id required - automatically unique per agent.
"""
import tkinter as tk
from tkinter import ttk
import threading
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_themes import DarkTheme
from BASE.tools.internal.voice.shared_voice_service import SharedVoiceService

try:
    from personality.bot_info import username
except ImportError:
    username = "User"


class VoiceManager:
    """
    Voice manager that uses SharedVoiceService
    
    MODIFIED: No longer creates its own audio stream or recognition model.
    Instead subscribes to centralized service.
    
    AUTOMATIC AGENT ID: Retrieves agent name from Config class automatically.
    Each agent's personality/bot_info.py provides unique identification.
    """

    __slots__ = ('message_queue', 'input_queue', 'logger', 'voice_enabled',
                 'agent_id', 'subscriber_id', 'voice_service', 'polling_thread',
                 'voice_button', 'voice_status', 'voice_volume_slider', 'voice_volume_label',
                 'sound_volume_slider', 'sound_volume_label', 'config')

    def __init__(self, message_queue, input_queue, logger, config=None):
        """
        Initialize voice manager
        
        Args:
            message_queue: Queue for GUI messages
            input_queue: Queue for user input
            logger: Logger instance
            config: Config instance (optional - will import if not provided)
        """
        self.message_queue = message_queue
        self.input_queue = input_queue
        self.logger = logger

        self.voice_enabled = False
        
        # AUTOMATIC: Get agent ID from config (personality/bot_info.py agentname)
        if config is None:
            from BASE.core.config import Config
            config = Config()
        self.config = config
        self.agent_id = config.agentname  # Automatically uses personality/bot_info.py
        
        self.subscriber_id = None
        
        self.voice_service = SharedVoiceService.get_instance()
        self.voice_service.set_logger(logger)
        
        self.polling_thread = None

        self.voice_button = None
        self.voice_status = None
        self.voice_volume_slider = None
        self.voice_volume_label = None
        self.sound_volume_slider = None
        self.sound_volume_label = None
        
        self.logger.system(f"VoiceManager initialized for agent: {self.agent_id}")

    def create_voice_panel(self, parent_frame):
        """Create voice control panel with volume controls"""
        voice_frame = ttk.LabelFrame(
            parent_frame, text="Voice & Audio Control", style="Dark.TLabelframe"
        )
        voice_frame.pack(fill=tk.X, pady=(0, 5))

        voice_controls = ttk.Frame(voice_frame)
        voice_controls.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.voice_button = ttk.Button(
            voice_controls,
            text="Start Voice Input",
            command=self.toggle_voice_input,
            width=20,
        )
        self.voice_button.pack(side=tk.LEFT, padx=(0, 10))

        self.voice_status = tk.Label(
            voice_controls,
            text="Voice: Disabled",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
        )
        self.voice_status.pack(side=tk.LEFT)
        
        self._create_volume_controls(voice_frame)

    def _create_volume_controls(self, parent_frame):
        """Create volume slider controls"""
        import personality.controls as controls
        
        volume_container = ttk.Frame(parent_frame)
        volume_container.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        voice_vol_frame = ttk.Frame(volume_container)
        voice_vol_frame.pack(fill=tk.X, pady=(0, 8))
        
        voice_label_frame = ttk.Frame(voice_vol_frame)
        voice_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        voice_icon = tk.Label(
            voice_label_frame,
            text="🎤",
            font=("Segoe UI", 12),
            background=DarkTheme.BG_DARKER,
            width=2
        )
        voice_icon.pack(side=tk.LEFT)
        
        voice_text = tk.Label(
            voice_label_frame,
            text="Voice",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=8,
            anchor="w"
        )
        voice_text.pack(side=tk.LEFT, padx=(5, 0))
        
        voice_slider_frame = ttk.Frame(voice_vol_frame)
        voice_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_volume_slider = tk.Scale(
            voice_slider_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_voice_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_PURPLE,
            highlightthickness=0,
            showvalue=0,
            length=150
        )
        self.voice_volume_slider.set(int(controls.VOICE_VOLUME * 100))
        self.voice_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_volume_label = tk.Label(
            voice_slider_frame,
            text=f"{int(controls.VOICE_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.voice_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        sound_vol_frame = ttk.Frame(volume_container)
        sound_vol_frame.pack(fill=tk.X)
        
        sound_label_frame = ttk.Frame(sound_vol_frame)
        sound_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        sound_icon = tk.Label(
            sound_label_frame,
            text="🔊",
            font=("Segoe UI", 12),
            background=DarkTheme.BG_DARKER,
            width=2
        )
        sound_icon.pack(side=tk.LEFT)
        
        sound_text = tk.Label(
            sound_label_frame,
            text="Sounds",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=8,
            anchor="w"
        )
        sound_text.pack(side=tk.LEFT, padx=(5, 0))
        
        sound_slider_frame = ttk.Frame(sound_vol_frame)
        sound_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sound_volume_slider = tk.Scale(
            sound_slider_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_sound_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_BLUE,
            highlightthickness=0,
            showvalue=0,
            length=150
        )
        self.sound_volume_slider.set(int(controls.SOUND_EFFECT_VOLUME * 100))
        self.sound_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sound_volume_label = tk.Label(
            sound_slider_frame,
            text=f"{int(controls.SOUND_EFFECT_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_BLUE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.sound_volume_label.pack(side=tk.LEFT, padx=(5, 0))

    def _on_voice_volume_change(self, value):
        import personality.controls as controls
        volume = int(value) / 100.0
        controls.VOICE_VOLUME = volume
        if self.voice_volume_label:
            self.voice_volume_label.config(text=f"{int(value)}%")

    def _on_sound_volume_change(self, value):
        import personality.controls as controls
        volume = int(value) / 100.0
        controls.SOUND_EFFECT_VOLUME = volume
        if self.sound_volume_label:
            self.sound_volume_label.config(text=f"{int(value)}%")

    def toggle_voice_input(self):
        """
        Toggle voice input - MODIFIED to use shared service
        """
        if not self.voice_enabled:
            try:
                status = self.voice_service.get_status()
                
                if not status['running']:
                    self.logger.system("Starting shared voice service...")
                    if not self.voice_service.start(preferred_backend="auto"):
                        raise RuntimeError("Failed to start shared voice service")
                
                self.subscriber_id = self.voice_service.subscribe(
                    agent_id=self.agent_id,
                    callback=None
                )
                
                status = self.voice_service.get_status()
                backend_name = f"{status['backend'].upper()} on {status['device'].upper()}"
                
                self.voice_enabled = True
                if self.voice_button:
                    self.voice_button.config(text="Stop Voice Input")
                if self.voice_status:
                    self.voice_status.config(
                        text=f"Voice: {backend_name} [SHARED]", 
                        foreground=DarkTheme.ACCENT_GREEN
                    )
                
                self.polling_thread = threading.Thread(
                    target=self._poll_voice_queue, 
                    daemon=True,
                    name=f"VoicePolling-{self.agent_id}"
                )
                self.polling_thread.start()
                
                self.logger.success(f"Voice input started for {self.agent_id}")
                self.logger.system(f"Total subscribers: {status['subscribers']}")

            except Exception as e:
                self.logger.error(f"Voice initialization error: {str(e)}")
                import traceback
                traceback.print_exc()
                self.voice_enabled = False
        else:
            self.stop_voice_input()

    def stop_voice_input(self):
        """Stop voice input - unsubscribe from shared service"""
        try:
            self.voice_enabled = False
            
            if self.voice_button:
                self.voice_button.config(text="Start Voice Input")
            if self.voice_status:
                self.voice_status.config(
                    text="Voice: Disabled", 
                    foreground=DarkTheme.FG_MUTED
                )
            
            if self.subscriber_id:
                self.voice_service.unsubscribe(self.subscriber_id)
                self.subscriber_id = None
            
            if self.polling_thread and self.polling_thread.is_alive():
                self.polling_thread.join(timeout=2.0)
            
            status = self.voice_service.get_status()
            
            if status['subscribers'] == 0:
                self.logger.system("No more subscribers - stopping shared service")
                self.voice_service.stop()
            
            self.logger.system("Voice input stopped")

        except Exception as e:
            self.logger.error(f"Error in stop_voice_input: {str(e)}")

    def _poll_voice_queue(self):
        """Poll voice queue from shared service"""
        try:
            self.logger.system(f"Voice polling started for {self.agent_id}")
            
            text_queue = self.voice_service.get_subscriber_queue(self.agent_id)
            if not text_queue:
                self.logger.error("Failed to get subscriber queue")
                return
            
            while self.voice_enabled:
                try:
                    text = text_queue.get(timeout=0.1)
                    
                    if text and len(text) >= 3:
                        self.message_queue.put(("voice_input", username, text))
                        self.input_queue.put(text)
                        self.logger.speech(f"[{self.agent_id}] Voice: {text}")
                        
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Voice polling error: {str(e)}")
            import traceback
            traceback.print_exc()


class VolumeControlPanel:
    """Standalone volume control panel"""

    __slots__ = ('parent', 'logger', 'controls', 'voice_volume_slider', 'voice_volume_label',
                 'sound_volume_slider', 'sound_volume_label')

    def __init__(self, parent, logger, controls_module):
        self.parent = parent
        self.logger = logger
        self.controls = controls_module
        self.voice_volume_slider = None
        self.voice_volume_label = None
        self.sound_volume_slider = None
        self.sound_volume_label = None
    
    def create_panel(self, show_title=True):
        """Create volume control panel"""
        if show_title:
            container = ttk.LabelFrame(
                self.parent,
                text="Audio Volume",
                style="Dark.TLabelframe"
            )
        else:
            container = ttk.Frame(self.parent)
        
        container.pack(fill=tk.X, pady=5)
        
        voice_frame = ttk.Frame(container)
        voice_frame.pack(fill=tk.X, padx=5, pady=(5, 8))
        
        tk.Label(
            voice_frame,
            text="Voice",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.voice_volume_slider = tk.Scale(
            voice_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_voice_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_PURPLE,
            highlightthickness=0,
            showvalue=0
        )
        self.voice_volume_slider.set(int(self.controls.VOICE_VOLUME * 100))
        self.voice_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_volume_label = tk.Label(
            voice_frame,
            text=f"{int(self.controls.VOICE_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.voice_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        sound_frame = ttk.Frame(container)
        sound_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(
            sound_frame,
            text="Sounds",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.sound_volume_slider = tk.Scale(
            sound_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_sound_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_BLUE,
            highlightthickness=0,
            showvalue=0
        )
        self.sound_volume_slider.set(int(self.controls.SOUND_EFFECT_VOLUME * 100))
        self.sound_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sound_volume_label = tk.Label(
            sound_frame,
            text=f"{int(self.controls.SOUND_EFFECT_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_BLUE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.sound_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        return container
    
    def _on_voice_volume_change(self, value):
        volume = int(value) / 100.0
        self.controls.VOICE_VOLUME = volume
        if self.voice_volume_label:
            self.voice_volume_label.config(text=f"{int(value)}%")
    
    def _on_sound_volume_change(self, value):
        volume = int(value) / 100.0
        self.controls.SOUND_EFFECT_VOLUME = volume
        if self.sound_volume_label:
            self.sound_volume_label.config(text=f"{int(value)}%")