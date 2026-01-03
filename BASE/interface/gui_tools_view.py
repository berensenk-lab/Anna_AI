# Filename: BASE/interface/gui_tools_view.py
"""
Dynamic Tools View - Creates GUI pages for installed tool components
Uses nested tabs - each tool gets its own dedicated tab
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from BASE.interface.gui_themes import DarkTheme
from BASE.interface.dynamic_tool_panel_loader import DynamicToolPanelLoader


class ToolsView:
    """
    Manages the Tools view with dynamically loaded tool panels
    Each installed tool with a component.py gets its own tab
    """

    __slots__ = ('parent', 'project_root', 'hot_reload_manager', 'panel_loader', 
                 'notebook', 'tool_tabs', 'tool_components')

    def __init__(self, parent, project_root, hot_reload_manager=None):
        """
        Initialize tools view
        
        Args:
            parent: Parent GUI instance
            project_root: Project root path
            hot_reload_manager: Optional HotReloadManager for tool reloading
        """
        self.parent = parent
        self.project_root = project_root
        self.hot_reload_manager = hot_reload_manager
        
        # Panel loader WITH hot-reload support
        self.panel_loader = DynamicToolPanelLoader(
            project_root=project_root,
            logger=parent.logger,
            hot_reload_manager=hot_reload_manager
        )
        
        # GUI elements
        self.notebook = None
        self.tool_tabs: Dict[str, ttk.Frame] = {}
        self.tool_components: Dict[str, Any] = {}
    
    def create_tools_view(self):
        """
        Create the Tools view with nested tabs for each tool
        
        Returns:
            Main frame containing notebook with individual tool tabs
        """
        # Main container
        main_container = ttk.Frame(self.parent.tools_view)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with info
        self._create_header(main_container)
        
        # Notebook for individual tool tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Discover and create tool panels (each tool gets its own tab)
        self._discover_and_create_panels()
        
        return main_container
    
    def _create_header(self, parent):
        """Create header with information"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🔧 Tool Panels",
            font=("Segoe UI", 11, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER
        )
        title_label.pack(side=tk.LEFT)
        
        # Info text
        info_label = tk.Label(
            header_frame,
            text="Each tool in its own tab • Auto-discovered from BASE/tools/installed/",
            font=("Segoe UI", 8, "italic"),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        )
        info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Refresh button
        refresh_button = ttk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_panels,
            width=12
        )
        refresh_button.pack(side=tk.RIGHT)
    
    def _discover_and_create_panels(self):
        """Discover tools and create individual tabs for those with components"""
        # Discover all tool panels
        panels = self.panel_loader.discover_tool_panels()
        
        if not panels:
            self._create_no_tools_message()
            return
        
        # Filter to only tools with components
        tools_with_components = [p for p in panels if p['has_component']]
        
        if not tools_with_components:
            self._create_no_components_message()
            return
        
        # Sort by display name, handling None values
        # FIX: Provide fallback for None display_name
        tools_with_components.sort(key=lambda x: x['display_name'] or x['tool_name'] or '')
        
        # Create individual tab for each tool
        for panel_info in tools_with_components:
            self._create_tool_tab(panel_info)
        
        # Log summary
        self.parent.logger.system(
            f"[Tools View] Created {len(tools_with_components)} tool tab(s)"
        )
    
    def _create_tool_tab(self, panel_info: Dict):
        """
        Create an individual tab for a single tool
        
        Args:
            panel_info: Tool panel metadata dict
        """
        tool_name = panel_info['tool_name']
        display_name = panel_info['display_name'] or tool_name.replace('_', ' ').title()
        icon = panel_info.get('icon', '🔧')
        component_path = panel_info['component_path']
        
        # Create tab frame with scrolling support
        tab_frame = ttk.Frame(self.notebook)
        
        # Add tab with icon and name
        tab_label = f"{icon} {display_name}"
        self.notebook.add(tab_frame, text=tab_label)
        
        # Create scrollable container for the tool panel
        canvas = tk.Canvas(tab_frame, bg=DarkTheme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure canvas to expand with window
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", configure_scroll_region)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Load and create the tool's component panel
        self._load_tool_component(scrollable_frame, panel_info)
    
    def _load_tool_component(self, parent, panel_info: Dict):
        """
        Load and create a tool's component in the given parent frame
        WITH RELOAD BUTTON at the top
        
        Args:
            parent: Parent frame
            panel_info: Tool panel metadata dict
        """
        tool_name = panel_info['tool_name']
        component_path = panel_info['component_path']
        
        # Create header frame with reload button
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 2))
        
        # Tool title
        title_label = tk.Label(
            header_frame,
            text=f"{panel_info.get('icon', '🔧')} {panel_info['display_name']}",
            font=("Segoe UI", 11, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER
        )
        title_label.pack(side=tk.LEFT)
        
        # Version label (if hot-reload available)
        if self.hot_reload_manager:
            version = self.hot_reload_manager.get_tool_version(tool_name)
            version_label = tk.Label(
                header_frame,
                text=f"v{version}",
                font=("Segoe UI", 8),
                foreground=DarkTheme.FG_MUTED,
                background=DarkTheme.BG_DARKER
            )
            version_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Reload button (right side)
        if self.hot_reload_manager:
            reload_btn = self.panel_loader.create_reload_button_for_tool(
                parent=header_frame,
                tool_name=tool_name
            )
            if reload_btn:
                reload_btn.pack(side=tk.RIGHT, padx=2)
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=5, pady=(2, 5))
        
        # Load component
        component = self.panel_loader.load_component(
            tool_name=tool_name,
            component_path=component_path,
            parent_gui=self.parent,
            ai_core=self.parent.ai_core
        )
        
        if not component:
            self.parent.logger.warning(
                f"[Tools View] Failed to load component for {tool_name}"
            )
            self._create_error_panel(parent, tool_name)
            return
        
        # Create panel frame
        try:
            panel_frame = component.create_panel(parent)
            
            # Store references
            self.tool_tabs[tool_name] = panel_frame
            self.tool_components[tool_name] = component
            
            self.parent.logger.system(
                f"[Tools View] Loaded tab for {tool_name}"
            )
        
        except Exception as e:
            self.parent.logger.error(
                f"[Tools View] Error creating panel for {tool_name}: {e}"
            )
            import traceback
            traceback.print_exc()
            self._create_error_panel(parent, tool_name, str(e))
    
    def _create_error_panel(self, parent, tool_name: str, error_msg: str = ""):
        """Create error message panel for failed tool loads"""
        error_frame = ttk.LabelFrame(
            parent,
            text=f"❌ Error Loading {tool_name}",
            style="Dark.TLabelframe"
        )
        error_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        error_text = f"Failed to load component for {tool_name}"
        if error_msg:
            error_text += f"\n\nError: {error_msg}"
        
        error_label = tk.Label(
            error_frame,
            text=error_text,
            font=("Segoe UI", 10),
            foreground=DarkTheme.ACCENT_RED,
            background=DarkTheme.BG_DARKER,
            justify=tk.LEFT,
            wraplength=500
        )
        error_label.pack(expand=True, padx=20, pady=20)
    
    def _create_no_tools_message(self):
        """Create message when no tools are installed"""
        message_frame = ttk.Frame(self.notebook)
        self.notebook.add(message_frame, text="No Tools")
        
        message_label = tk.Label(
            message_frame,
            text="No tools found in BASE/tools/installed/",
            font=("Segoe UI", 10),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        )
        message_label.pack(expand=True)
    
    def _create_no_components_message(self):
        """Create message when no tool components are available"""
        message_frame = ttk.Frame(self.notebook)
        self.notebook.add(message_frame, text="No Components")
        
        message_label = tk.Label(
            message_frame,
            text=(
                "Tools are installed but none have GUI components.\n\n"
                "To add a GUI component, create a component.py file\n"
                "in the tool's directory with a create_component() function."
            ),
            font=("Segoe UI", 10),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
            justify=tk.CENTER
        )
        message_label.pack(expand=True)
    
    def _refresh_panels(self):
        """
        Refresh all tool panels with ACTUAL hot-reload
        This reloads the Python modules, not just the GUI
        """
        self.parent.logger.system("[Tools View] 🔄 Starting hot-reload refresh...")
        
        # Get list of active tools
        active_tools = []
        if hasattr(self.parent, 'ai_core') and hasattr(self.parent.ai_core, 'tool_manager'):
            active_tools = self.parent.ai_core.tool_manager.get_active_tool_names()
            self.parent.logger.system(f"[Tools View] Found {len(active_tools)} active tools")
        
        # Hot-reload each active tool if hot-reload manager available
        if self.hot_reload_manager and active_tools:
            import asyncio
            
            self.parent.logger.system("[Tools View] Hot-reloading Python modules...")
            
            async def reload_all_tools():
                """Reload all active tools sequentially"""
                success_count = 0
                fail_count = 0
                
                for tool_name in active_tools:
                    self.parent.logger.system(f"[Hot-Reload] Reloading {tool_name}...")
                    
                    try:
                        success = await self.hot_reload_manager.reload_tool(
                            tool_name, 
                            notify_gui=False
                        )
                        
                        if success:
                            self.parent.logger.success(f"[Hot-Reload] ✅ {tool_name} reloaded")
                            success_count += 1
                        else:
                            self.parent.logger.error(f"[Hot-Reload] ❌ {tool_name} reload failed")
                            fail_count += 1
                    
                    except Exception as e:
                        self.parent.logger.error(f"[Hot-Reload] ❌ {tool_name} error: {e}")
                        fail_count += 1
                
                return success_count, fail_count
            
            # Get event loop from AI Core
            if hasattr(self.parent.ai_core, 'main_loop') and self.parent.ai_core.main_loop:
                # Run reload in event loop
                future = asyncio.run_coroutine_threadsafe(
                    reload_all_tools(),
                    self.parent.ai_core.main_loop
                )
                
                try:
                    # Wait for reload to complete (with timeout)
                    success_count, fail_count = future.result(timeout=30.0)
                    
                    self.parent.logger.system(
                        f"[Hot-Reload] Module reload complete: "
                        f"{success_count} succeeded, {fail_count} failed"
                    )
                
                except TimeoutError:
                    self.parent.logger.error("[Hot-Reload] ⏱️ Reload timed out after 30s")
                
                except Exception as e:
                    self.parent.logger.error(f"[Hot-Reload] Error during reload: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                self.parent.logger.warning("[Hot-Reload] No event loop - skipping module reload")
        
        elif self.hot_reload_manager and not active_tools:
            self.parent.logger.system("[Hot-Reload] No active tools to reload")
        
        elif not self.hot_reload_manager:
            self.parent.logger.warning("[Hot-Reload] Hot-reload manager not available")
        
        # Now refresh GUI panels (redraw with updated code)
        self.parent.logger.system("[Tools View] Refreshing GUI panels...")
        
        # Cleanup existing components
        cleanup_count = 0
        for tool_name, component in list(self.tool_components.items()):
            if hasattr(component, 'cleanup'):
                try:
                    component.cleanup()
                    cleanup_count += 1
                except Exception as e:
                    self.parent.logger.warning(
                        f"[Tools View] Error cleaning up {tool_name}: {e}"
                    )
        
        # if cleanup_count > 0:
        #     self.parent.logger.system(f"[Tools View] Cleaned up {cleanup_count} components")
        
        # Clear references
        self.tool_tabs.clear()
        self.tool_components.clear()
        
        # Clear notebook tabs
        tab_count = len(self.notebook.tabs())
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        if tab_count > 0:
            self.parent.logger.system(f"[Tools View] Removed {tab_count} GUI tabs")
        
        # Re-discover and create individual tool tabs (now with reloaded code)
        self.parent.logger.system("[Tools View] Discovering and creating new panels...")
        self._discover_and_create_panels()
        
        # Final summary
        new_tab_count = len(self.notebook.tabs())
        self.parent.logger.success(
            f"[Tools View] ✅ Complete refresh finished! "
            f"({new_tab_count} tool panels active)"
        )
    
    def cleanup(self):
        """Cleanup all tool components"""
        self.panel_loader.cleanup_all()
        self.tool_tabs.clear()
        self.tool_components.clear()