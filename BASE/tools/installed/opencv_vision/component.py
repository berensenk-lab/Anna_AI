# Filename: BASE/tools/installed/opencv_vision/component.py
"""
OpenCV Vision Tool - GUI Component
Dynamic GUI panel for continuous screen monitoring configuration
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from BASE.interface.gui_themes import DarkTheme


class OpenCVVisionComponent:
    """GUI component for OpenCV Vision tool with prompt customization"""
    
    def __init__(self, parent_gui, ai_core, logger):
        self.parent_gui = parent_gui
        self.ai_core = ai_core
        self.logger = logger
        
        self.vision_tool = None
        
        self.panel_frame = None
        self.status_label = None
        self.fps_label = None
        self.capture_count_label = None
        self.analysis_label = None
        self.prompt_text = None
        self.fps_var = None
        self.interval_var = None
        self.width_var = None
        self.height_var = None
        self.threshold_var = None
        
        self.last_update = 0
        
        self.default_prompt = (
            "You are monitoring a screen for an AI agent. "
            "Provide a detailed description of what's currently visible on the screen. "
            "This is captured from the user's desktop, and may be a screenshot of an image, "
            "a game, an application, text, or other media. "
            "If characters, text, objects, or other noteworthy items appear, describe them. "
            "Describe any observed interactions between the objects in the image. "
            "If any UI elements are present, provide details about them. "
            "If uncertainty about a detail exists, omit that detail. "
            "Describe only what is visible and do not invent details. "
            "The description should include an overall impression as well as specific details. "
            "Keep the description under 1000 characters. Respond with only the description "
            "of what is visible on the screen."
        )
    
    def create_panel(self, parent_frame):
        self.panel_frame = ttk.LabelFrame(
            parent_frame,
            text="OpenCV Vision Monitor",
            style="Dark.TLabelframe"
        )
        self.panel_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self._create_status_section()
        self._create_performance_section()
        self._create_config_section()
        self._create_prompt_section()
        self._create_action_buttons()
        
        self._update_status()
        self._start_auto_refresh()
        
        return self.panel_frame
    
    def _create_status_section(self):
        status_frame = ttk.Frame(self.panel_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            status_frame,
            text="[Status]",
            style="TLabel"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_label = tk.Label(
            status_frame,
            text="Checking...",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        info_button = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 10),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
            cursor="hand2"
        )
        info_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self._create_tooltip(
            info_button,
            "OpenCV Vision Features:\n\n"
            "• High-performance screen capture (10-50ms)\n"
            "• Configurable FPS (1-60)\n"
            "• Non-blocking threaded capture\n"
            "• Change detection optimization\n"
            "• Automatic thought buffer injection\n"
            "• Customizable analysis prompts\n\n"
            "Perfect for:\n"
            "- VTuber streaming awareness\n"
            "- Real-time game monitoring\n"
            "- Desktop activity tracking\n\n"
            "Tip: Lower FPS = less CPU overhead"
        )
    
    def _create_performance_section(self):
        perf_frame = ttk.LabelFrame(
            self.panel_frame,
            text="Performance Metrics",
            style="Dark.TLabelframe"
        )
        perf_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        metrics_container = ttk.Frame(perf_frame)
        metrics_container.pack(fill=tk.X, padx=5, pady=5)
        
        fps_row = ttk.Frame(metrics_container)
        fps_row.pack(fill=tk.X, pady=2)
        ttk.Label(fps_row, text="Current FPS:", width=20).pack(side=tk.LEFT)
        self.fps_label = tk.Label(
            fps_row,
            text="0.0 / 0",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_GREEN,
            background=DarkTheme.BG_DARKER
        )
        self.fps_label.pack(side=tk.LEFT)
        
        capture_row = ttk.Frame(metrics_container)
        capture_row.pack(fill=tk.X, pady=2)
        ttk.Label(capture_row, text="Captures:", width=20).pack(side=tk.LEFT)
        self.capture_count_label = tk.Label(
            capture_row,
            text="0",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        )
        self.capture_count_label.pack(side=tk.LEFT)
        
        analysis_row = ttk.Frame(metrics_container)
        analysis_row.pack(fill=tk.X, pady=2)
        ttk.Label(analysis_row, text="Analysis Interval:", width=20).pack(side=tk.LEFT)
        self.analysis_label = tk.Label(
            analysis_row,
            text="0.0s",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        )
        self.analysis_label.pack(side=tk.LEFT)
    
    def _create_config_section(self):
        config_frame = ttk.LabelFrame(
            self.panel_frame,
            text="Configuration",
            style="Dark.TLabelframe"
        )
        config_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        config_container = ttk.Frame(config_frame)
        config_container.pack(fill=tk.X, padx=5, pady=5)
        
        fps_row = ttk.Frame(config_container)
        fps_row.pack(fill=tk.X, pady=2)
        ttk.Label(fps_row, text="Target FPS (1-60):", width=20).pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=10)
        fps_spin = ttk.Spinbox(
            fps_row,
            from_=1,
            to=60,
            textvariable=self.fps_var,
            width=8,
            font=("Segoe UI", 9)
        )
        fps_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        interval_row = ttk.Frame(config_container)
        interval_row.pack(fill=tk.X, pady=2)
        ttk.Label(interval_row, text="Analysis Interval (s):", width=20).pack(side=tk.LEFT)
        self.interval_var = tk.DoubleVar(value=5.0)
        interval_spin = ttk.Spinbox(
            interval_row,
            from_=1.0,
            to=60.0,
            increment=1.0,
            textvariable=self.interval_var,
            width=8,
            font=("Segoe UI", 9)
        )
        interval_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        width_row = ttk.Frame(config_container)
        width_row.pack(fill=tk.X, pady=2)
        ttk.Label(width_row, text="Capture Width:", width=20).pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=1024)
        width_spin = ttk.Spinbox(
            width_row,
            from_=320,
            to=1920,
            increment=64,
            textvariable=self.width_var,
            width=8,
            font=("Segoe UI", 9)
        )
        width_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        height_row = ttk.Frame(config_container)
        height_row.pack(fill=tk.X, pady=2)
        ttk.Label(height_row, text="Capture Height:", width=20).pack(side=tk.LEFT)
        self.height_var = tk.IntVar(value=768)
        height_spin = ttk.Spinbox(
            height_row,
            from_=240,
            to=1080,
            increment=48,
            textvariable=self.height_var,
            width=8,
            font=("Segoe UI", 9)
        )
        height_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        threshold_row = ttk.Frame(config_container)
        threshold_row.pack(fill=tk.X, pady=2)
        ttk.Label(threshold_row, text="Change Threshold:", width=20).pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=50000)
        threshold_spin = ttk.Spinbox(
            threshold_row,
            from_=10000,
            to=200000,
            increment=10000,
            textvariable=self.threshold_var,
            width=8,
            font=("Segoe UI", 9)
        )
        threshold_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        apply_btn = ttk.Button(
            config_container,
            text="Apply Configuration",
            command=self._apply_config
        )
        apply_btn.pack(pady=(5, 0))
    
    def _create_prompt_section(self):
        prompt_frame = ttk.LabelFrame(
            self.panel_frame,
            text="Vision Analysis Prompt",
            style="Dark.TLabelframe"
        )
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        instructions = tk.Label(
            prompt_frame,
            text="Customize how the AI analyzes screen captures:",
            font=("Segoe UI", 8, "italic"),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
            anchor=tk.W
        )
        instructions.pack(fill=tk.X, padx=5, pady=(5, 3))
        
        text_container = ttk.Frame(prompt_frame)
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.prompt_text = scrolledtext.ScrolledText(
            text_container,
            height=10,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_DARK,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.ACCENT_GREEN,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=DarkTheme.BORDER,
            highlightcolor=DarkTheme.ACCENT_PURPLE
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        
        button_container = ttk.Frame(prompt_frame)
        button_container.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        save_btn = tk.Button(
            button_container,
            text="[Save] Apply Prompt",
            command=self._save_prompt,
            font=("Segoe UI", 9, "bold"),
            bg=DarkTheme.ACCENT_PURPLE,
            fg="white",
            activebackground=DarkTheme.BUTTON_HOVER,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        reset_btn = tk.Button(
            button_container,
            text="[Reset] Reset to Default",
            command=self._reset_prompt,
            font=("Segoe UI", 9),
            bg=DarkTheme.BUTTON_BG,
            fg=DarkTheme.FG_PRIMARY,
            activebackground=DarkTheme.BUTTON_HOVER,
            activeforeground=DarkTheme.FG_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5
        )
        reset_btn.pack(side=tk.LEFT)
        
        self._load_current_prompt()
    
    def _create_action_buttons(self):
        action_frame = ttk.Frame(self.panel_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        capture_btn = tk.Button(
            action_frame,
            text="[Camera] Capture & Analyze Now",
            command=self._force_capture,
            font=("Segoe UI", 9, "bold"),
            bg=DarkTheme.ACCENT_GREEN,
            fg="white",
            activebackground=DarkTheme.BUTTON_HOVER,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        capture_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = tk.Button(
            action_frame,
            text="[Refresh] Refresh Status",
            command=self._update_status,
            font=("Segoe UI", 9),
            bg=DarkTheme.BUTTON_BG,
            fg=DarkTheme.FG_PRIMARY,
            activebackground=DarkTheme.BUTTON_HOVER,
            activeforeground=DarkTheme.FG_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        refresh_btn.pack(side=tk.LEFT)
    
    def _load_current_prompt(self):
        """Load current prompt from tool or use default"""
        self.vision_tool = self._get_vision_tool()
        
        if self.vision_tool and hasattr(self.vision_tool, 'analysis_prompt'):
            current_prompt = self.vision_tool.analysis_prompt
        else:
            current_prompt = self.default_prompt
        
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", current_prompt)
    
    def _save_prompt(self):
        """Save custom prompt to tool"""
        self.vision_tool = self._get_vision_tool()
        
        if not self.vision_tool:
            self.logger.error("[OpenCV Vision] Tool not available - cannot save prompt")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        if not prompt:
            self.logger.warning("[OpenCV Vision] Empty prompt - using default")
            prompt = self.default_prompt
        
        self.vision_tool.analysis_prompt = prompt
        
        self.logger.success(f"[OpenCV Vision] [Confirmed] Custom prompt applied ({len(prompt)} chars)")
    
    def _reset_prompt(self):
        """Reset prompt to default"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", self.default_prompt)
        
        self._save_prompt()
        
        self.logger.system("[OpenCV Vision] Prompt reset to default")
    
    def _apply_config(self):
        """Apply configuration changes to tool"""
        self.vision_tool = self._get_vision_tool()
        
        if not self.vision_tool:
            self.logger.error("[OpenCV Vision] Tool not available - cannot apply config")
            return
        
        fps = self.fps_var.get()
        interval = self.interval_var.get()
        width = self.width_var.get()
        height = self.height_var.get()
        threshold = self.threshold_var.get()
        
        self.vision_tool.target_fps = max(1, min(60, fps))
        self.vision_tool.analysis_interval = max(1.0, interval)
        self.vision_tool.capture_width = max(320, min(1920, width))
        self.vision_tool.capture_height = max(240, min(1080, height))
        self.vision_tool.change_threshold = max(10000, threshold)
        
        self.logger.success(
            f"[OpenCV Vision] [Confirmed] Configuration applied: "
            f"{fps} FPS, {interval}s interval, {width}x{height}, threshold {threshold}"
        )
        
        self._update_status()
    
    def _force_capture(self):
        """Force immediate capture and analysis"""
        self.vision_tool = self._get_vision_tool()
        
        if not self.vision_tool:
            self.logger.error("[OpenCV Vision] Tool not available")
            return
        
        if self.ai_core.main_loop:
            import asyncio
            
            async def capture_async():
                try:
                    result = await self.vision_tool.execute('capture_now', [])
                    
                    if result.get('success'):
                        self.logger.success("[OpenCV Vision] [Confirmed] Capture complete")
                    else:
                        self.logger.error(f"[OpenCV Vision] Capture failed: {result.get('content')}")
                
                except Exception as e:
                    self.logger.error(f"[OpenCV Vision] Capture error: {e}")
            
            asyncio.run_coroutine_threadsafe(capture_async(), self.ai_core.main_loop)
        
        self.logger.tool("[OpenCV Vision] [Camera] Forcing immediate capture...")
    
    def _update_status(self):
        """Update status display"""
        import time
        current_time = time.time()
        
        if current_time - self.last_update < 0.5:
            return
        
        self.last_update = current_time
        
        self.vision_tool = self._get_vision_tool()
        
        if not self.vision_tool:
            self.status_label.config(
                text="Tool Not Enabled",
                foreground=DarkTheme.FG_MUTED
            )
            self.fps_label.config(text="0.0 / 0")
            self.capture_count_label.config(text="0")
            self.analysis_label.config(text="0.0s")
            return
        
        if not self.vision_tool.is_available():
            self.status_label.config(
                text="[Warning] Libraries Not Available",
                foreground=DarkTheme.ACCENT_RED
            )
            return
        
        status = self.vision_tool.get_status()
        
        if status['capture_running']:
            self.status_label.config(
                text="[Confirmed] Active - Monitoring Screen",
                foreground=DarkTheme.ACCENT_GREEN
            )
        else:
            self.status_label.config(
                text="[Warning] Tool Enabled but Not Capturing",
                foreground=DarkTheme.ACCENT_ORANGE
            )
        
        self.fps_label.config(
            text=f"{status['current_fps']:.1f} / {status['target_fps']}"
        )
        self.capture_count_label.config(
            text=str(status['capture_count'])
        )
        self.analysis_label.config(
            text=f"{status['analysis_interval']:.1f}s"
        )
        
        self.fps_var.set(status['target_fps'])
        self.interval_var.set(status['analysis_interval'])
        
        monitor = status.get('monitor', {})
        if monitor:
            self.width_var.set(self.vision_tool.capture_width)
            self.height_var.set(self.vision_tool.capture_height)
        
        if hasattr(self.vision_tool, 'change_threshold'):
            self.threshold_var.set(self.vision_tool.change_threshold)
    
    def _start_auto_refresh(self):
        """Start automatic status refresh"""
        self._update_status()
        self.panel_frame.after(2000, self._start_auto_refresh)
    
    def _get_vision_tool(self):
        """Get OpenCV vision tool instance"""
        if not hasattr(self.ai_core, 'tool_manager'):
            return None
        
        tool_manager = self.ai_core.tool_manager
        
        if 'opencv_vision' not in tool_manager._active_tools:
            return None
        
        return tool_manager._active_tools.get('opencv_vision')
    
    def _create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(bg=DarkTheme.BG_DARK)
            
            label = tk.Label(
                tooltip,
                text=text,
                background=DarkTheme.BG_DARK,
                foreground=DarkTheme.FG_PRIMARY,
                font=("Segoe UI", 9),
                wraplength=400,
                padx=8,
                pady=4,
                justify=tk.LEFT
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def cleanup(self):
        """Cleanup component resources"""
        self.logger.tool("[OpenCV Vision] Component cleaned up")


def create_component(parent_gui, ai_core, logger):
    """Factory function for dynamic loading"""
    return OpenCVVisionComponent(parent_gui, ai_core, logger)