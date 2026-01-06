# BASE/handlers/internal_tool_manager.py
"""
Internal Tool Manager - Service-per-Tool Architecture
Manages mutually exclusive service categories
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import asyncio


class InternalToolManager:
    """
    Manages internal tools with service category enforcement
    
    Service Categories (mutually exclusive):
    - tts: Only one TTS tool active at a time
    - voice_input: Only one voice input tool active at a time
    - audio_effects: Can coexist with others
    """
    
    __slots__ = (
        'project_root', 'config', 'controls', 'logger',
        '_tools', '_tool_metadata', '_service_categories',
        '_control_to_tool_map', 'hub_client'
    )
    
    def __init__(self, project_root: Path, config, controls, logger=None):
        self.project_root = project_root
        self.config = config
        self.controls = controls
        self.logger = logger
        
        self._tools: Dict[str, Any] = {}
        self._tool_metadata: Dict[str, Dict] = {}
        
        # Service category tracking
        self._service_categories: Dict[str, str] = {}  # service_type -> active_tool_name
        
        # Control variable mapping
        self._control_to_tool_map: Dict[str, str] = {}
        
        # Integrations
        self.hub_client = None
    
    async def discover_and_initialize(self):
        """Discover and initialize internal tools"""
        tools_dir = self.project_root / 'BASE' / 'tools' / 'internal'
        
        if not tools_dir.exists():
            if self.logger:
                self.logger.warning("[Internal Tools] Directory not found")
            return
        
        # Discovery phase
        discovered = []
        
        for tool_dir in tools_dir.iterdir():
            if not tool_dir.is_dir() or tool_dir.name.startswith('_'):
                continue
            
            if tool_dir.name == 'shared':  # Skip shared utilities
                continue
            
            info_file = tool_dir / 'information.json'
            tool_file = tool_dir / 'tool.py'
            
            if not info_file.exists() or not tool_file.exists():
                continue
            
            # Load metadata
            with open(info_file, 'r') as f:
                metadata = json.load(f)
            
            tool_name = metadata.get('tool_name')
            
            if not tool_name:
                continue
            
            self._tool_metadata[tool_name] = metadata
            discovered.append((tool_name, tool_dir, tool_file, metadata))
            
            # Build control mapping
            control_var = metadata.get('control_variable_name')
            if control_var:
                self._control_to_tool_map[control_var] = tool_name
            
            if self.logger:
                service_type = metadata.get('service_type', 'unknown')
                self.logger.system(
                    f"[Internal Tools] Discovered {tool_name} ({service_type})"
                )
        
        # Sort by priority (higher priority loaded first)
        discovered.sort(key=lambda x: x[3].get('priority', 0), reverse=True)
        
        # Initialization phase
        for tool_name, tool_dir, tool_file, metadata in discovered:
            should_enable = self._should_enable_tool(metadata)
            
            if should_enable:
                await self._load_tool(tool_name, tool_dir, tool_file, metadata)
    
    def _should_enable_tool(self, metadata: Dict) -> bool:
        """
        Determine if tool should be enabled based on control variables
        
        Supports:
        - enabled_when_true: Enable when control = True
        - enabled_when_false: Enable when control = False
        """
        control_var = metadata.get('control_variable_name')
        control_logic = metadata.get('control_logic', 'enabled_when_true')
        
        if not control_var:
            return False
        
        control_value = getattr(self.controls, control_var, False)
        
        if control_logic == 'enabled_when_true':
            return control_value is True
        elif control_logic == 'enabled_when_false':
            return control_value is False
        else:
            return False
    
    async def _load_tool(
        self,
        tool_name: str,
        tool_dir: Path,
        tool_file: Path,
        metadata: Dict
    ):
        """Load and initialize a tool with service category enforcement"""
        service_type = metadata.get('service_type')
        
        # Check if another tool in same category is active
        if service_type and service_type in self._service_categories:
            current_active = self._service_categories[service_type]
            
            if self.logger:
                self.logger.system(
                    f"[Internal Tools] Disabling {current_active} "
                    f"to enable {tool_name}"
                )
            
            # Stop current tool
            await self._unload_tool(current_active)
        
        try:
            # Dynamic import
            import importlib.util
            import sys
            
            spec = importlib.util.spec_from_file_location(
                f"internal_tool_{tool_name}",
                str(tool_file)
            )
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            # Find tool class (XTTSTool, Pyttsx3Tool, etc.)
            tool_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    attr_name.endswith('Tool') and 
                    attr_name not in ['BaseTool', 'InternalToolInterface']):
                    tool_class = attr
                    break
            
            if not tool_class:
                if self.logger:
                    self.logger.error(f"[Internal Tools] No tool class in {tool_name}")
                return
            
            # Instantiate
            tool_instance = tool_class(
                config=self.config,
                controls=self.controls,
                logger=self.logger
            )
            
            # Inject dependencies
            if self.hub_client and hasattr(tool_instance, 'set_hub_client'):
                tool_instance.set_hub_client(self.hub_client)
            
            # Initialize
            success = await tool_instance.initialize()
            
            if success:
                self._tools[tool_name] = tool_instance
                
                # Register service category
                if service_type:
                    self._service_categories[service_type] = tool_name
                
                if self.logger:
                    self.logger.success(
                        f"[Internal Tools] {tool_name} initialized and ACTIVE"
                    )
            else:
                if self.logger:
                    self.logger.error(
                        f"[Internal Tools] {tool_name} initialization failed"
                    )
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Internal Tools] Error loading {tool_name}: {e}")
            import traceback
            traceback.print_exc()
    
    async def _unload_tool(self, tool_name: str):
        """Unload and cleanup a tool"""
        tool = self._tools.get(tool_name)
        
        if not tool:
            return
        
        try:
            await tool.cleanup()
            
            # Remove from active tools
            del self._tools[tool_name]
            
            # Remove from service category tracking
            metadata = self._tool_metadata.get(tool_name)
            if metadata:
                service_type = metadata.get('service_type')
                if service_type and self._service_categories.get(service_type) == tool_name:
                    del self._service_categories[service_type]
            
            if self.logger:
                self.logger.system(f"[Internal Tools] {tool_name} unloaded")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Internal Tools] Error unloading {tool_name}: {e}")
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get tool by name"""
        return self._tools.get(tool_name)
    
    def get_active_tts_tool(self) -> Optional[Any]:
        """Get currently active TTS tool"""
        active_name = self._service_categories.get('tts')
        if active_name:
            return self._tools.get(active_name)
        return None
    
    def get_active_voice_input_tool(self) -> Optional[Any]:
        """Get currently active voice input tool"""
        active_name = self._service_categories.get('voice_input')
        if active_name:
            return self._tools.get(active_name)
        return None
    
    async def handle_control_change(self, control_name: str, new_value: bool):
        """
        Handle control variable changes
        
        Automatically switches between tools in same service category
        """
        # Find tool affected by this control
        tool_name = self._control_to_tool_map.get(control_name)
        
        if not tool_name:
            return
        
        metadata = self._tool_metadata.get(tool_name)
        if not metadata:
            return
        
        should_enable = self._should_enable_tool(metadata)
        is_currently_active = tool_name in self._tools
        
        if should_enable and not is_currently_active:
            # Enable this tool
            tool_dir = self.project_root / 'BASE' / 'tools' / 'internal' / tool_name
            tool_file = tool_dir / 'tool.py'
            
            await self._load_tool(tool_name, tool_dir, tool_file, metadata)
        
        elif not should_enable and is_currently_active:
            # Disable this tool
            await self._unload_tool(tool_name)
    
    def set_hub_client(self, hub_client):
        """Inject Voice Hub client into all tools"""
        self.hub_client = hub_client
        
        for tool in self._tools.values():
            if hasattr(tool, 'set_hub_client'):
                tool.set_hub_client(hub_client)
    
    async def cleanup_all(self):
        """Cleanup all tools"""
        for tool_name in list(self._tools.keys()):
            await self._unload_tool(tool_name)
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_status(self) -> Dict:
        """Get manager status"""
        return {
            'discovered_tools': len(self._tool_metadata),
            'active_tools': len(self._tools),
            'active_by_category': self._service_categories.copy(),
            'tool_list': list(self._tools.keys())
        }