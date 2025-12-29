# Filename: BASE/core/dynamic_control_initializer.py
"""
Dynamic Control Variable Initializer
Reads all information.json files and creates control variables with correct defaults.
MUST run before GUI initialization.
"""
from pathlib import Path
import json


class DynamicControlInitializer:
    """Initialize control variables from tool information.json files"""
    
    __slots__ = ('project_root', 'controls_module', 'logger', 'tools_dir')
    
    def __init__(self, project_root: Path, controls_module, logger=None):
        self.project_root = project_root
        self.controls_module = controls_module
        self.logger = logger
        self.tools_dir = project_root / 'BASE' / 'tools' / 'installed'
    
    def initialize_all_tool_controls(self) -> int:
        """
        Initialize all tool control variables from information.json files
        
        Returns:
            Number of control variables initialized
        """
        if not self.tools_dir.exists():
            if self.logger:
                self.logger.warning(f"[Control Init] Tools directory not found: {self.tools_dir}")
            return 0
        
        # Minimize attribute lookups
        controls = self.controls_module
        hasattr_func = hasattr
        setattr_func = setattr
        
        initialized = []
        
        for tool_dir in self.tools_dir.iterdir():
            if not tool_dir.is_dir() or tool_dir.name[0] in ('_', '.'):
                continue
            
            info_file = tool_dir / 'information.json'
            if not info_file.exists():
                continue
            
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                
                control_var = info.get('control_variable_name')
                if not control_var or hasattr_func(controls, control_var):
                    continue
                
                default_value = info.get('control_variable_value', False)
                tool_name = info.get('tool_name', tool_dir.name)
                
                setattr_func(controls, control_var, default_value)
                initialized.append((control_var, default_value, tool_name))
            
            except:
                pass
        
        if self.logger and initialized:
            self.logger.system(f"[Control Init] Initialized {len(initialized)} tool control variables")
            for control_var, default_value, tool_name in initialized:
                self.logger.system(f"  • {control_var} = {default_value} (from {tool_name})")
        
        return len(initialized)