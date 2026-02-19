# Filename: BASE/tools/installed/unity/component.py
"""
Unity Animation Tool - GUI Component
Dynamic GUI panel for Unity VRM character animation control
"""
import tkinter as tk
from tkinter import ttk
from BASE.interface.gui_themes import DarkTheme
from datetime import datetime


class UnityAnimationComponent:
    """
    GUI component for Unity Animation tool
    Provides interface for controlling VRM character emotions and animations
    """

    def __init__(self,parent_gui,ai_core,logger):
        self.parent_gui=parent_gui
        self.ai_core=ai_core
        self.logger=logger
        self.theme=self._get_theme()
        self.unity_tool=None
        self.panel_frame=None
        self.status_label=None
        self.avatar_label=None
        self.emotion_buttons=[]
        self.gesture_buttons=[]
        self.preset_buttons=[]
        self.loop_buttons=[]
        self.intensity_var=None
        self.log_text=None
        self.connected=False
        self.update_job=None
        self.last_command_time=0
        self.emotions=['happy','sad','angry','surprised','neutral','relaxed']
        self.gestures=['wave','nod','shake_head','head_shake','bow','shrug','think','point','reach','being_cocky','angry_idle']
        self.preset_animations=[]
        self.loop_animations=[]

    def _get_theme(self):
        if hasattr(self.parent_gui,'theme_manager'):
            return self.parent_gui.theme_manager.get_theme()
        from BASE.interface.gui_themes import DarkTheme
        return DarkTheme

    def create_panel(self,parent_frame):
        self.panel_frame=ttk.LabelFrame(parent_frame,text="[Animation] Unity VRM Animation",style="Dark.TLabelframe")
        self.panel_frame.pack(fill=tk.BOTH,expand=True,pady=(5,0))
        self._create_status_section()
        self._create_intensity_section()
        self._create_emotions_section()
        self._create_animations_section()
        self._create_control_section()
        self._create_log_section()

        # Start status updates
        self._schedule_status_update()

        return self.panel_frame

    def _create_status_section(self):
        status_frame=ttk.Frame(self.panel_frame)
        status_frame.pack(fill=tk.X,padx=5,pady=5)
        status_left=ttk.Frame(status_frame)
        status_left.pack(side=tk.LEFT,fill=tk.X,expand=True)
        self.status_label=tk.Label(status_left,text="Not Connected",font=("Segoe UI",9,"bold"),foreground=self.theme.FG_MUTED,background=self.theme.BG_DARKER,anchor=tk.W)
        self.status_label.pack(side=tk.LEFT,padx=(0,10))
        self.avatar_label=tk.Label(status_left,text="Avatar: --",font=("Segoe UI",9),foreground=self.theme.FG_SECONDARY,background=self.theme.BG_DARKER,anchor=tk.W)
        self.avatar_label.pack(side=tk.LEFT)

        # Refresh button
        status_right = ttk.Frame(status_frame)
        status_right.pack(side=tk.RIGHT)
        refresh_btn=ttk.Button(status_right,text="Refresh",command=self._refresh_status,width=12)
        refresh_btn.pack(side=tk.LEFT,padx=2)
        reconnect_btn=ttk.Button(status_right,text="[Connect] Connect",command=self._connect_unity,width=12)
        reconnect_btn.pack(side=tk.LEFT,padx=2)

    def _create_intensity_section(self):
        """Create intensity control section"""
        intensity_frame = ttk.Frame(self.panel_frame)
        intensity_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(
            intensity_frame,
            text="Intensity:",
            style="TLabel"
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.intensity_var = tk.DoubleVar(value=0.8)

        intensity_scale = ttk.Scale(
            intensity_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.intensity_var,
            length=200
        )
        intensity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        intensity_label = tk.Label(
            intensity_frame,
            textvariable=self.intensity_var,
            font=("Consolas", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=4
        )
        intensity_label.pack(side=tk.LEFT)

        # Update label format
        def update_intensity_label(*args):
            intensity_label.config(text=f"{self.intensity_var.get():.2f}")

        self.intensity_var.trace('w', update_intensity_label)
        update_intensity_label()

    def _create_emotions_section(self):
        emotions_frame=ttk.LabelFrame(self.panel_frame,text="[Emotion] Emotions",style="Dark.TLabelframe")
        emotions_frame.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        info_label=tk.Label(emotions_frame,text="Express character emotions and feelings",font=("Segoe UI",8,"italic"),foreground=self.theme.FG_MUTED,background=self.theme.BG_DARKER)
        info_label.pack(fill=tk.X,padx=5,pady=(5,3))
        self.emotions_container=ttk.Frame(emotions_frame)
        self.emotions_container.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        self.emotion_buttons=[]

    def _create_gestures_section(self):
        gestures_frame=ttk.LabelFrame(self.panel_frame,text="[Gesture] Gestures",style="Dark.TLabelframe")
        gestures_frame.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        info_label=tk.Label(gestures_frame,text="Procedural gestures and body language",font=("Segoe UI",8,"italic"),foreground=self.theme.FG_MUTED,background=self.theme.BG_DARKER)
        info_label.pack(fill=tk.X,padx=5,pady=(5,3))
        buttons_container=ttk.Frame(gestures_frame)
        buttons_container.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        self.gesture_buttons=[]
        gesture_icons={'wave':'[Wave]','nod':'[Nod]','shake_head':'[No]','head_shake':'[Shake]','bow':'[Bow]','shrug':'[Shrug]','think':'[Think]','point':'[Point]','reach':'[Reach]','being_cocky':'[Cocky]','angry_idle':'[Angry]'}
        row_frame=None
        for i,gesture in enumerate(self.gestures):
            if i%4==0:
                row_frame=ttk.Frame(buttons_container)
                row_frame.pack(fill=tk.X,pady=2)
            icon=gesture_icons.get(gesture,'[Hand]')
            text=f"{icon} {gesture.replace('_',' ').title()}"
            btn=ttk.Button(row_frame,text=text,command=lambda g=gesture:self._execute_gesture(g),width=15)
            btn.pack(side=tk.LEFT,padx=2,expand=True,fill=tk.X)
            self.gesture_buttons.append(btn)

    def _create_loops_section(self):
        self.loops_frame=ttk.LabelFrame(self.panel_frame,text="[Loop] Loop Animations",style="Dark.TLabelframe")
        self.loops_frame.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        info_label=tk.Label(self.loops_frame,text="Continuous looping animations from Animator",font=("Segoe UI",8,"italic"),foreground=self.theme.FG_MUTED,background=self.theme.BG_DARKER)
        info_label.pack(fill=tk.X,padx=5,pady=(5,3))
        self.loops_container=ttk.Frame(self.loops_frame)
        self.loops_container.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        self.loop_buttons=[]

    def _create_presets_section(self):
        self.presets_frame=ttk.LabelFrame(self.panel_frame,text="[Preset] One-Shot Animations",style="Dark.TLabelframe")
        self.presets_frame.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        info_label=tk.Label(self.presets_frame,text="One-time animations from Animator",font=("Segoe UI",8,"italic"),foreground=self.theme.FG_MUTED,background=self.theme.BG_DARKER)
        info_label.pack(fill=tk.X,padx=5,pady=(5,3))
        self.presets_container=ttk.Frame(self.presets_frame)
        self.presets_container.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        self.preset_buttons=[]

    def _create_control_section(self):
        control_frame=ttk.LabelFrame(self.panel_frame,text="[Settings] Custom Command",style="Dark.TLabelframe")
        control_frame.pack(fill=tk.X,padx=5,pady=(0,5))
        input_frame=ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X,padx=5,pady=5)
        self.command_type_var=tk.StringVar(value='emotion')
        emotion_radio=ttk.Radiobutton(input_frame,text="Emotion",variable=self.command_type_var,value='emotion')
        emotion_radio.pack(side=tk.LEFT,padx=(0,10))
        gesture_radio=ttk.Radiobutton(input_frame,text="Gesture",variable=self.command_type_var,value='gesture')
        gesture_radio.pack(side=tk.LEFT,padx=(0,10))
        preset_radio=ttk.Radiobutton(input_frame,text="Preset",variable=self.command_type_var,value='preset')
        preset_radio.pack(side=tk.LEFT,padx=(0,10))
        self.custom_value_var=tk.StringVar()
        value_entry=ttk.Entry(input_frame,textvariable=self.custom_value_var,width=20)
        value_entry.pack(side=tk.LEFT,padx=(0,5),fill=tk.X,expand=True)
        execute_btn=ttk.Button(input_frame,text="Execute",command=self._execute_custom,width=12)
        execute_btn.pack(side=tk.LEFT)
        value_entry.bind('<Return>',lambda e:self._execute_custom())

    def _create_log_section(self):
        log_frame=ttk.LabelFrame(self.panel_frame,text="[Log] Activity Log",style="Dark.TLabelframe")
        log_frame.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))
        self.log_text=tk.Text(log_frame,height=6,font=("Consolas",8),background=self.theme.BG_DARKER,foreground=self.theme.FG_PRIMARY,wrap=tk.WORD,state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        self.log_text.tag_config('info',foreground=self.theme.FG_SECONDARY)
        self.log_text.tag_config('success',foreground=self.theme.ACCENT_GREEN)
        self.log_text.tag_config('error',foreground=self.theme.ACCENT_RED)
        self.log_text.tag_config('cmd',foreground=self.theme.ACCENT_BLUE)

    def _execute_emotion(self,emotion:str):
        intensity=self.intensity_var.get()
        self._execute_command('emotion',[emotion,intensity])

    def _execute_gesture(self,gesture:str):
        self._execute_command('gesture',[gesture])

    def _execute_preset(self,preset:str):
        self._execute_command('preset',[preset])

    def _execute_custom(self):
        """Execute custom command"""
        command_type = self.command_type_var.get()
        value = self.custom_value_var.get().strip()

        if not value:
            self._add_log("No value entered", 'error')
            return

        intensity = self.intensity_var.get()
        self._execute_command(command_type, [value, intensity])

        # Clear entry
        self.custom_value_var.set("")

    def _execute_command(self,command:str,args:list):
        self.unity_tool=self._get_unity_tool()
        if not self.unity_tool:
            self._add_log("Unity tool not enabled",'error')
            return

        if not self.unity_tool.is_available():
            self._add_log("Unity not connected - attempting to connect...", 'info')
            self._connect_unity()
            return

        # Format args display
        if len(args) > 1:
            args_display = f"{args[0]} (intensity: {args[1]:.2f})"
        else:
            args_display = str(args[0])

        self._add_log(f"Sending: {command} {args_display}", 'cmd')

        # Execute via AI Core
        if self.ai_core.main_loop:
            import asyncio

            async def execute_async():
                result = await self.unity_tool.execute(command, args)

                if result.get('success'):
                    message = result.get('content', 'Success')
                    self._add_log(message, 'success')
                else:
                    error = result.get('content', 'Command failed')
                    self._add_log(error, 'error')

                    # Show guidance if available
                    guidance = result.get('guidance')
                    if guidance:
                        self._add_log(f"  -> {guidance}",'info')
            asyncio.run_coroutine_threadsafe(execute_async(),self.ai_core.main_loop)

    def _connect_unity(self):
        """Attempt to connect to Unity"""
        self.unity_tool = self._get_unity_tool()

        if not self.unity_tool:
            self._add_log("Unity tool not initialized", 'error')
            return

        self._add_log("Connecting to Unity...", 'info')

        if self.ai_core.main_loop:
            import asyncio

            async def connect_async():
                result = await self.unity_tool.execute('connect', [])

                if result.get('success'):
                    self._add_log("Connected to Unity!", 'success')
                    self._update_status()
                else:
                    error=result.get('content','Connection failed')
                    self._add_log(error,'error')
            asyncio.run_coroutine_threadsafe(connect_async(),self.ai_core.main_loop)

    def _refresh_status(self):
        """Force status refresh"""
        self._add_log("Refreshing status...", 'info')
        self._update_status()

    def _update_status(self):
        """Update status display"""
        self.unity_tool = self._get_unity_tool()

        if not self.unity_tool:
            self._update_status_disconnected()
            return

        # Get status from tool
        status = self.unity_tool.get_status()

        if status.get('connected'):
            self._update_status_connected(status)

            emotions_changed=False
            gestures_changed=False
            presets_changed=False

            if status.get('emotions'):
                if status['emotions']!=self.emotions:
                    self.emotions=status['emotions']
                    emotions_changed=True
                elif len(self.emotion_buttons)==0:
                    emotions_changed=True

            if status.get('gestures'):
                if status['gestures']!=self.gestures:
                    self.gestures=status['gestures']
                    gestures_changed=True

            if status.get('preset_animations'):
                all_presets=status['preset_animations']
                loops=[p for p in all_presets if p.endswith('_loop')]
                one_shots=[p for p in all_presets if not p.endswith('_loop')]

                self._add_log(f"Retrieved {len(all_presets)} animations: {len(loops)} loops, {len(one_shots)} one-shots",'info')

                if loops!=self.loop_animations:
                    self.loop_animations=loops
                    presets_changed=True
                elif len(self.loop_buttons)==0 and len(loops)>0:
                    self.loop_animations=loops
                    presets_changed=True

                if one_shots!=self.preset_animations:
                    self.preset_animations=one_shots
                    presets_changed=True
                elif len(self.preset_buttons)==0 and len(one_shots)>0:
                    self.preset_animations=one_shots
                    presets_changed=True

            if emotions_changed:
                self._rebuild_emotion_buttons()

            if status.get('animations') and status['animations'] != self.animations:
                self.animations = status['animations']
                self._rebuild_animation_buttons()
        else:
            self._update_status_disconnected()

    def _update_status_connected(self,status:dict):
        self.connected=True
        self.status_label.config(text="Connected",foreground=self.theme.ACCENT_GREEN)
        avatar_name=status.get('avatar_name','Unknown')
        vrm_status="VRM OK" if status.get('vrm_connected') else "No VRM"
        self.avatar_label.config(text=f"Avatar: {avatar_name} | {vrm_status}",foreground=self.theme.FG_PRIMARY)

    def _update_status_disconnected(self):
        self.connected=False
        self.status_label.config(text="Not Connected",foreground=self.theme.FG_MUTED)
        self.avatar_label.config(text="Avatar: --",foreground=self.theme.FG_MUTED)

    def _rebuild_emotion_buttons(self):
        """Rebuild emotion buttons with updated list"""
        # Clear existing buttons
        for btn in self.emotion_buttons:
            btn.destroy()
        self.emotion_buttons.clear()

        # Note: Full rebuild would require recreating the entire section
        # For now, just log the change
        self._add_log(f"Emotions updated: {len(self.emotions)} available", 'info')

    def _rebuild_animation_buttons(self):
        """Rebuild animation buttons with updated list"""
        # Clear existing buttons
        for btn in self.animation_buttons:
            btn.destroy()
        self.animation_buttons.clear()

        # Note: Full rebuild would require recreating the entire section
        # For now, just log the change
        self._add_log(f"Animations updated: {len(self.animations)} available", 'info')

    def _add_log(self, message: str, tag='info'):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)

        # Limit log size
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 100:
            self.log_text.delete('1.0', '51.0')

        self.log_text.config(state=tk.DISABLED)

    def _schedule_status_update(self):
        """Schedule periodic status updates"""
        if self.panel_frame and self.panel_frame.winfo_exists():
            self._update_status()
            # Update every 5 seconds
            self.update_job = self.panel_frame.after(5000, self._schedule_status_update)

    def _get_unity_tool(self):
        """Get Unity tool instance from AI Core"""
        if not hasattr(self.ai_core, 'tool_manager'):
            return None

        tool_manager = self.ai_core.tool_manager

        # Check if tool is active
        if 'unity' not in tool_manager._active_tools:
            return None

        return tool_manager._active_tools.get('unity')

    def cleanup(self):
        """Cleanup component resources"""
        # Cancel scheduled updates
        if self.update_job:
            try:
                self.panel_frame.after_cancel(self.update_job)
            except:
                pass

        if self.logger:
            self.logger.system("[Unity] Component cleaned up")


def create_component(parent_gui,ai_core,logger):
    return UnityAnimationComponent(parent_gui,ai_core,logger)
