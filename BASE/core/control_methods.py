# Filename: BASE/core/control_methods.py
"""
Control Manager - Dynamic Control Variable Management
FIXED: Filters tool controls vs feature flags to prevent spurious tool lifecycle calls
"""
from typing import Optional, Dict, Any


class ControlManager:
    """
    Manages runtime control of agent features
    
    CRITICAL FIX: Distinguishes between:
    - Tool controls (USE_WIKI_SEARCH, USE_WARUDO_ANIMATION, etc.) → notify tool manager
    - Feature flags (USE_SYSTEM_PROMPT, SAVE_MEMORY, etc.) → internal only
    """
    __slots__ = (
        'controls_module', 'logger', 'config',
        '_ai_core_ref', '_tool_manager_ref', '_defaults',
        '_tool_control_vars'
    )
    
    def __init__(self, controls_module, logger, config=None):
        """
        Initialize control manager
        
        Args:
            controls_module: personality.controls module
            logger: Logger instance (MUST already have config set)
            config: Config instance (MUST be same instance as logger.config)
        """
        self.controls_module = controls_module
        self.logger = logger
        self.config = config
        
        self._ai_core_ref = None
        self._tool_manager_ref = None
        
        # Cache of actual tool control variables (populated when tool_manager is set)
        self._tool_control_vars = set()
        
        # ===================================================================
        # CRITICAL: Verify config instance matches logger's config
        # ===================================================================
        if config is not None and hasattr(logger, 'config') and logger.config is not None:
            if id(config) != id(logger.config):
                error_msg = (
                    f"CRITICAL: Config instance mismatch!\n"
                    f"  ControlManager config: {id(config)}\n"
                    f"  Logger config: {id(logger.config)}\n"
                    f"These MUST be the same instance!"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            else:
                logger.system(
                    f"[ControlManager] [SUCCESS] Config instance verified: {id(config)}"
                )
        elif config is None:
            logger.warning("[ControlManager] No config provided - logging controls unavailable")
        elif not hasattr(logger, 'config') or logger.config is None:
            logger.warning("[ControlManager] Logger has no config - this should not happen!")
        
        # Store defaults
        self._defaults = self._capture_defaults()
    
    def _capture_defaults(self) -> Dict[str, Any]:
        """Capture current control values as defaults"""
        defaults = {}
        for attr in dir(self.controls_module):
            if attr.isupper() and not attr.startswith('_'):
                defaults[attr] = getattr(self.controls_module, attr)
        return defaults
    
    # ========================================================================
    # DEPENDENCY INJECTION
    # ========================================================================
    
    def set_ai_core(self, ai_core):
        """Inject AI core reference for cognitive loop control"""
        self._ai_core_ref = ai_core
        self.logger.system("[ControlManager] AI Core reference set")
    
    def set_tool_manager(self, tool_manager):
        """
        Inject tool manager and discover which controls are for tools
        
        CRITICAL: This builds the filter by discovering actual tool controls
        """
        self._tool_manager_ref = tool_manager
        
        if not tool_manager:
            self.logger.system("[ControlManager] Tool manager reference set")
            return
        
        # Discover which control variables correspond to ACTUAL tools
        try:
            all_metadata = tool_manager.get_all_tool_metadata()
            
            for tool_name, metadata in all_metadata.items():
                control_var = metadata.get('control_variable')
                
                if control_var:
                    self._tool_control_vars.add(control_var)
                    if self.logger:
                        self.logger.system(
                            f"[Control Manager] Registered tool control: {control_var} → {tool_name}"
                        )
            
            if self._tool_control_vars:
                self.logger.system(
                    f"[Control Manager] Tracking {len(self._tool_control_vars)} tool controls"
                )
                self.logger.system(
                    f"[Control Manager] Tool controls: {', '.join(sorted(self._tool_control_vars))}"
                )
            else:
                self.logger.warning(
                    "[Control Manager] No tool controls discovered - tools won't start on toggle"
                )
        
        except Exception as e:
            self.logger.error(f"[Control Manager] Failed to discover tool controls: {e}")
        
        self.logger.system("[ControlManager] Tool manager reference set")
    
    def _is_tool_control(self, control_name: str) -> bool:
        """
        Check if a control variable corresponds to an actual tool
        
        Args:
            control_name: Control variable name
            
        Returns:
            True if this is a tool control, False if it's a feature flag
        """
        return control_name in self._tool_control_vars
    
    # ========================================================================
    # SPECIAL HANDLERS
    # ========================================================================
    
    def handle_continuous_thinking_toggle(self, new_value: bool) -> bool:
        """
        Handle toggling of continuous thinking
        
        Args:
            new_value: New state (True = enabled, False = disabled)
            
        Returns:
            True if operation succeeded, False otherwise
        """
        if not self._ai_core_ref:
            self.logger.error("[Continuous Thinking] No AI Core reference")
            return False
        
        ai_core = self._ai_core_ref
        
        # Get thought processor
        if not hasattr(ai_core, 'processing_delegator') or not ai_core.processing_delegator:
            self.logger.error("[Continuous Thinking] No processing delegator")
            return False
        
        thought_processor = ai_core.processing_delegator.thought_processor
        
        if new_value:
            # START continuous thinking
            if thought_processor.cognitive_loop and thought_processor.cognitive_loop.is_running:
                self.logger.system("[Continuous Thinking] Already running")
                return True
            
            try:
                # Ensure event loop and AI core reference are set
                thought_processor.event_loop = ai_core.main_loop
                thought_processor.set_ai_core_reference(ai_core)
                
                # Start the loop
                thought_processor.start_continuous_thinking()
                
                self.logger.system("[SUCCESS] [Continuous Thinking] STARTED - Agent thinking autonomously")
                return True
                
            except Exception as e:
                self.logger.error(f"[Continuous Thinking] Failed to start: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        else:
            # STOP continuous thinking
            if not thought_processor.cognitive_loop or not thought_processor.cognitive_loop.is_running:
                self.logger.system("[Continuous Thinking] Already stopped")
                return True
            
            try:
                import asyncio
                
                # Stop via async call
                asyncio.run_coroutine_threadsafe(
                    thought_processor.stop_continuous_thinking(),
                    ai_core.main_loop
                )
                
                self.logger.system("[SUCCESS] [Continuous Thinking] STOPPED - Agent will only respond to input")
                return True
                
            except Exception as e:
                self.logger.error(f"[Continuous Thinking] Failed to stop: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def restart_cognition(self) -> bool:
        """
        Manually restart the cognitive loop after a crash
        This resets the crash counter and restarts regardless of crash count
        
        Returns:
            True if restart initiated successfully, False otherwise
        """
        if not self._ai_core_ref:
            self.logger.error("[Restart] No AI Core reference")
            return False
        
        ai_core = self._ai_core_ref
        
        # Get thought processor
        if not hasattr(ai_core, 'processing_delegator') or not ai_core.processing_delegator:
            self.logger.error("[Restart] No processing delegator")
            return False
        
        thought_processor = ai_core.processing_delegator.thought_processor
        
        if not hasattr(thought_processor, 'cognitive_loop') or not thought_processor.cognitive_loop:
            self.logger.error("[Restart] No cognitive loop manager")
            return False
        
        try:
            import asyncio
            
            self.logger.system("[Restart] Initiating manual cognitive loop restart...")
            
            # Call restart via async
            future = asyncio.run_coroutine_threadsafe(
                thought_processor.cognitive_loop.restart_cognition(),
                ai_core.main_loop
            )
            
            # Wait briefly for restart to initiate
            future.result(timeout=5.0)
            
            self.logger.system("[SUCCESS] [Restart] Cognitive loop restart initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"[Restart] Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========================================================================
    # MAIN CONTROL API
    # ========================================================================
    
    def toggle_feature(self, feature_name: str) -> Optional[bool]:
        """
        Toggle a control feature with special handling
        
        FIXED: Only notifies tool manager for actual tool controls
        
        Args:
            feature_name: Name of control variable
            
        Returns:
            New value if successful, None if failed
        """
        # SPECIAL HANDLING: Continuous thinking
        if feature_name == "ENABLE_CONTINUOUS_THINKING":
            current_value = getattr(self.controls_module, feature_name, False)
            new_value = not current_value
            
            success = self.handle_continuous_thinking_toggle(new_value)
            
            if success:
                setattr(self.controls_module, feature_name, new_value)
                # Don't notify tool manager - this isn't a tool
                return new_value
            else:
                self.logger.error(f"[{feature_name}] Toggle failed - keeping current state")
                return current_value
        
        # SPECIAL HANDLING: Logging controls (stored in Config)
        logging_controls = {
            'LOG_TOOL_EXECUTION', 'LOG_PROMPT_CONSTRUCTION',
            'LOG_REACTIVE_PROMPT', 'LOG_REFLECTIVE_PROMPT',
            'LOG_PROACTIVE_PROMPT', 'LOG_RESPONSIVE_PROMPT', 'LOG_ACTION_PROMPT',
            'LOG_RESPONSE_PROCESSING', 'LOG_SYSTEM_INFORMATION', 'SHOW_CHAT'
        }
        
        if feature_name in logging_controls:
            if not self.config:
                self.logger.error(f"[{feature_name}] No config reference - cannot toggle")
                return None
            
            current_value = getattr(self.config, feature_name, False)
            new_value = not current_value
            
            setattr(self.config, feature_name, new_value)
            
            # Verify the update worked
            verified_value = getattr(self.config, feature_name)
            if verified_value != new_value:
                self.logger.error(f"[{feature_name}] Update verification FAILED")
                return None
            
            status = "enabled" if new_value else "disabled"
            self.logger.system(f"[{feature_name}] {status} (config {id(self.config)})")
            
            # Don't notify tool manager - these are logging flags
            return new_value
        
        # STANDARD TOGGLE: Regular control variables
        if not hasattr(self.controls_module, feature_name):
            self.logger.error(f"Control variable not found: {feature_name}")
            return None
        
        current_value = getattr(self.controls_module, feature_name)
        
        if not isinstance(current_value, bool):
            self.logger.error(f"Cannot toggle non-boolean: {feature_name}")
            return None
        
        new_value = not current_value
        setattr(self.controls_module, feature_name, new_value)
        
        # CRITICAL FIX: Only notify tool manager for actual tool controls
        self._notify_control_change(feature_name, new_value)
        
        return new_value
    
    def set_feature(self, feature_name: str, value: bool) -> bool:
        """
        Set a control feature to specific value
        
        FIXED: Only notifies tool manager for actual tool controls
        
        Args:
            feature_name: Name of control variable
            value: Value to set
            
        Returns:
            True if successful
        """
        # SPECIAL HANDLING: Continuous thinking
        if feature_name == "ENABLE_CONTINUOUS_THINKING":
            current_value = getattr(self.controls_module, feature_name, False)
            
            if current_value == value:
                return True  # Already at desired state
            
            success = self.handle_continuous_thinking_toggle(value)
            
            if success:
                setattr(self.controls_module, feature_name, value)
                # Don't notify tool manager
            
            return success
        
        # SPECIAL HANDLING: Logging controls
        logging_controls = {
            'LOG_TOOL_EXECUTION', 'LOG_PROMPT_CONSTRUCTION',
            'LOG_RESPONSE_PROCESSING', 'LOG_SYSTEM_INFORMATION', 'SHOW_CHAT'
        }
        
        if feature_name in logging_controls:
            if not self.config:
                self.logger.error(f"[{feature_name}] No config reference")
                return False
            
            setattr(self.config, feature_name, value)
            
            verified = getattr(self.config, feature_name)
            if verified != value:
                self.logger.error(f"[{feature_name}] Set verification failed")
                return False
            
            self.logger.system(f"[{feature_name}] Set to {value}")
            # Don't notify tool manager
            return True
        
        # STANDARD SET: Regular controls
        if not hasattr(self.controls_module, feature_name):
            self.logger.error(f"Control variable not found: {feature_name}")
            return False
        
        setattr(self.controls_module, feature_name, value)
        
        # CRITICAL FIX: Only notify tool manager for actual tool controls
        self._notify_control_change(feature_name, value)
        
        return True
    
    def get_feature(self, feature_name: str) -> Optional[bool]:
        """Get current value of a control feature"""
        # Check logging controls first
        logging_controls = {
            'LOG_TOOL_EXECUTION', 'LOG_PROMPT_CONSTRUCTION',
            'LOG_RESPONSE_PROCESSING', 'LOG_SYSTEM_INFORMATION', 'SHOW_CHAT'
        }
        
        if feature_name in logging_controls and self.config:
            return getattr(self.config, feature_name, False)
        
        # Check regular controls
        if hasattr(self.controls_module, feature_name):
            return getattr(self.controls_module, feature_name)
        
        return None
    
    def reset_to_defaults(self):
        """Reset all controls to their default values"""
        for feature_name, default_value in self._defaults.items():
            self.set_feature(feature_name, default_value)
        
        self.logger.system("All controls reset to defaults")
    
    # ========================================================================
    # NOTIFICATIONS
    # ========================================================================
    
    def _notify_control_change(self, feature_name: str, new_value: bool):
        """
        Notify dependent systems of control change
        
        CRITICAL FIX: Only notifies tool manager for actual tool controls
        """
        # Determine control type
        is_tool = self._is_tool_control(feature_name)
        control_type = "Tool" if is_tool else "Feature"
        status = "enabled" if new_value else "disabled"
        
        # Log with control type
        self.logger.system(f"[Control] {feature_name} {status} ({control_type})")
        
        # CRITICAL FIX: Only notify tool manager for actual tool controls
        if is_tool:
            if self._tool_manager_ref:
                self.logger.system(
                    f"[Control] Notifying tool manager: {feature_name} → {status}"
                )
                try:
                    self._tool_manager_ref.handle_control_update(feature_name, new_value)
                except Exception as e:
                    self.logger.warning(f"Tool manager notification failed: {e}")
            else:
                self.logger.warning(
                    f"[Control] Tool manager not available for {feature_name}"
                )
        else:
            self.logger.system(
                f"[Control] Internal feature flag - no tool lifecycle needed"
            )
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    def get_all_controls(self) -> Dict[str, bool]:
        """Get all control variables and their current values"""
        controls = {}
        
        # Regular controls
        for attr in dir(self.controls_module):
            if attr.isupper() and not attr.startswith('_'):
                value = getattr(self.controls_module, attr)
                if isinstance(value, bool):
                    controls[attr] = value
        
        # Logging controls from config
        if self.config:
            logging_controls = {
                'LOG_TOOL_EXECUTION', 'LOG_PROMPT_CONSTRUCTION',
                'LOG_RESPONSE_PROCESSING', 'LOG_SYSTEM_INFORMATION', 'SHOW_CHAT'
            }
            for ctrl in logging_controls:
                if hasattr(self.config, ctrl):
                    controls[ctrl] = getattr(self.config, ctrl)
        
        return controls
    
    def get_tool_controls_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all tool controls
        
        Returns:
            Dict with tool control info
        """
        if not self._tool_manager_ref:
            return {}
        
        status = {}
        
        for control_var in self._tool_control_vars:
            enabled = getattr(self.controls_module, control_var, False)
            
            # Find tool name for this control
            tool_name = None
            all_metadata = self._tool_manager_ref.get_all_tool_metadata()
            
            for t_name, metadata in all_metadata.items():
                if metadata.get('control_variable') == control_var:
                    tool_name = t_name
                    break
            
            status[control_var] = {
                'enabled': enabled,
                'tool_name': tool_name,
                'is_tool_control': True
            }
        
        return status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get control manager statistics"""
        all_features = self.get_all_controls()
        enabled_count = sum(1 for v in all_features.values() if v is True)
        
        return {
            'total_controls': len(all_features),
            'enabled_count': enabled_count,
            'disabled_count': len(all_features) - enabled_count,
            'tool_controls_tracked': len(self._tool_control_vars),
            'tool_controls': sorted(list(self._tool_control_vars))
        }
    
    def get_continuous_thinking_status(self) -> Dict[str, Any]:
        """Get detailed status of continuous thinking"""
        if not self._ai_core_ref:
            return {'available': False, 'reason': 'No AI Core reference'}
        
        try:
            thought_processor = self._ai_core_ref.processing_delegator.thought_processor
            
            if not thought_processor.cognitive_loop:
                return {
                    'available': True,
                    'running': False,
                    'control_enabled': getattr(
                        self.controls_module, 
                        'ENABLE_CONTINUOUS_THINKING', 
                        False
                    )
                }
            
            loop = thought_processor.cognitive_loop
            stats = loop.get_statistics()
            
            return {
                'available': True,
                'running': loop.is_running,
                'control_enabled': getattr(
                    self.controls_module, 
                    'ENABLE_CONTINUOUS_THINKING', 
                    False
                ),
                'statistics': stats
            }
            
        except Exception as e:
            return {
                'available': False,
                'reason': f'Error: {e}'
            }