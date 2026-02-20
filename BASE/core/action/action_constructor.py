# Filename: BASE/core/action/action_constructor.py
"""
Action Mode Prompt Constructor - UPDATED
=========================================
Focus: Execute tools with correct parameters based on thought chain

Changes:
- Clearer output format instructions
- Emphasis on parameter extraction from thoughts
- Detailed tool instructions dynamically retrieved
"""

from typing import List, Dict, Optional, Any
from BASE.core.action.action_parts import ActionPromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts


class ActionConstructor:
    """Constructs prompts for action mode (tool execution)"""

    __slots__ = ('tool_manager', 'logger', 'parts', 'personality')
    
    def __init__(self, tool_manager=None, logger=None):
        """
        Initialize action constructor
        
        Args:
            tool_manager: ToolManager instance for tool instructions
            logger: Optional logger instance
        """
        self.tool_manager = tool_manager
        self.logger = logger
        
        # Initialize prompt parts
        self.parts = ActionPromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_action_prompt(
        self,
        thought_chain: List[str],
        planned_actions: List[Dict[str, Any]],
        context_parts: List[str] = None,
        action_context: Optional[str] = None
    ) -> str:
        """
        Build complete action execution prompt - UPDATED
        
        Args:
            thought_chain: Recent thoughts (for parameter extraction)
            planned_actions: Tool actions to execute
            context_parts: Additional context
            action_context: Why these actions were chosen
        
        Returns:
            Complete action mode prompt
        """
        context_parts = context_parts or []
        
        sections = []
        
        # 1. Mode instructions (FIRST - sets the task)
        sections.append(self.parts.get_mode_instructions())
        
        # 2. Recent thoughts (for parameter context)
        sections.append(self._format_thought_chain(thought_chain))
        
        # 3. Planned actions (what we're executing)
        sections.append(self._format_planned_actions(planned_actions))
        
        # 4. Detailed tool instructions (dynamically retrieved)
        if self.tool_manager and planned_actions:
            tool_instructions = self._get_tool_instructions_for_actions(planned_actions)
            if tool_instructions:
                sections.append(tool_instructions)
        
        # 5. Action context (why these actions)
        if action_context:
            sections.append(f"\n## ACTION CONTEXT\n\n{action_context}")
        
        # 6. Execution principles
        sections.append(self.parts.get_execution_principles())
        
        # 7. Additional context
        if context_parts:
            sections.append(self._format_additional_context(context_parts))
        
        # 8. Output format (CLEAR instructions)
        sections.append(self.parts.get_output_format())
        
        prompt = "\n".join(sections)
        
        if self.logger:
            log_full = bool(
                getattr(getattr(self.logger, 'config', None), 'LOG_FULL_PROMPTS', False)
            )
            if log_full:
                self.logger.action(prompt)
            else:
                self.logger.action(f"[Action Prompt] length={len(prompt)} chars")

        return prompt
    
    def _format_thought_chain(self, thoughts: List[str]) -> str:
        """Format recent thoughts for action context"""
        if not thoughts:
            return "\n## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
        
        # Use recent thoughts (last 10 for action context)
        recent = thoughts[-10:] if len(thoughts) > 10 else thoughts
        formatted = "\n".join([f"- {t}" for t in recent])
        
        thought_count = len(recent)
        return f"\n## YOUR RECENT THOUGHTS ({thought_count} thoughts)\n\n{formatted}"
    
    def _format_planned_actions(self, actions: List[Dict[str, Any]]) -> str:
        """
        Format planned actions for execution - UPDATED
        
        Args:
            actions: List of action dictionaries with 'tool' and 'args' keys
        
        Returns:
            Formatted actions section
        """
        if not actions:
            return "\n## PLANNED ACTIONS\n\nNo actions planned."
        
        lines = ["\n## PLANNED ACTIONS\n"]
        lines.append("These are the tools you decided to use. Now execute them with proper parameters.\n")
        
        for i, action in enumerate(actions, 1):
            tool_name = action.get('tool', 'unknown')
            args = action.get('args', [])
            
            lines.append(f"**[Action {i}]** `{tool_name}`")
            
            # Show current args if provided
            if args:
                if isinstance(args, list) and args:
                    args_str = ", ".join([f'"{a}"' for a in args])
                    lines.append(f"  - Current args: [{args_str}]")
                elif isinstance(args, dict):
                    lines.append(f"  - Current args: {args}")
                else:
                    lines.append(f"  - Args: {args}")
            else:
                lines.append("  - No args provided yet")
        
        lines.append("\n**Your Task:** Format these tool calls with correct parameters based on your thoughts.")
        
        return "\n".join(lines)
    
    def _get_tool_instructions_for_actions(self, actions: List[Dict[str, Any]]) -> str:
        """
        Get detailed tool instructions for specific tools being executed - UPDATED
        
        Args:
            actions: List of action dictionaries
        
        Returns:
            Formatted tool instructions section
        """
        if not self.tool_manager or not actions:
            return ""
        
        # Extract unique tool names from actions
        tool_names = set()
        for action in actions:
            tool_name = action.get('tool', '')
            if tool_name:
                # Handle both "tool_name" and "category.tool_name" formats
                base_name = tool_name.split('.')[0] if '.' in tool_name else tool_name
                tool_names.add(base_name)
        
        if not tool_names:
            return ""
        
        # Build detailed instructions using ToolInstructionBuilder
        from BASE.handlers.tool_instruction_builder import ToolInstructionBuilder
        
        builder = ToolInstructionBuilder(
            tool_manager=self.tool_manager,
            logger=self.logger
        )
        
        # Get instructions for the specific tools being used
        instructions = builder.build_retrieved_tool_instructions(list(tool_names))
        
        if instructions:
            if self.logger:
                self.logger.system(
                    f"[Action Constructor] Retrieved instructions for "
                    f"{len(tool_names)} tools: {', '.join(tool_names)}"
                )
            return instructions
        
        return ""
    
    def _format_additional_context(self, context_parts: List[str]) -> str:
        """Format additional context"""
        formatted = "\n\n".join(context_parts)
        return f"\n## ADDITIONAL CONTEXT\n\n{formatted}"
