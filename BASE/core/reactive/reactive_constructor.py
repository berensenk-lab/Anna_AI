# Filename: BASE/core/reactive/reactive_constructor.py
"""
Reactive Thinking Prompt Constructor - OPTIMIZED
=================================================
Minimal tool instructions in cognitive modes - detailed docs only in ACTION mode

Prompt Components:
1. Personality (core identity + thinking style)
2. Thought chain (recent thoughts for continuity)
3. Available tool list (minimal overview only)
4. Incoming data (events to process)
5. Response guidance (how to think about events)

Focus: Real-time processing of new information
Tool execution: Handled by separate ACTION mode
"""

from typing import List, Optional, Any
from BASE.core.reactive.reactive_parts import ReactivePromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts


class ReactiveConstructor:
    """Constructs prompts for reactive thinking"""

    __slots__ = ('tool_manager', 'logger', 'parts', 'personality')
    
    def __init__(self, tool_manager=None, logger=None):
        self.tool_manager = tool_manager
        self.logger = logger
        self.parts = ReactivePromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_reactive_prompt(
        self,
        thought_chain: List[str],
        raw_events: List[Any],
        context_parts: List[str] = None,
        last_user_msg: Optional[str] = None,
        pending_actions: Optional[str] = None,
        has_vision: bool = False
    ) -> str:
        """Build complete reactive thinking prompt"""
        context_parts = context_parts or []
        sections = []
        
        # 1. Personality injection
        sections.append(self.personality.get_unified_personality())
        
        # 1.5. Current context (if available)
        current_ctx = self.personality.format_current_context()
        if current_ctx:
            sections.append(current_ctx)
        
        # 2. Recent thoughts
        sections.append(self._format_thought_chain(thought_chain))
        
        # 3. Mode instructions
        sections.append(self.parts.get_mode_instructions())
        
        # 4. Tool list (minimal overview only)
        if self.tool_manager:
            tool_list = self._build_minimal_tool_list()
            if tool_list:
                sections.append(tool_list)
        
        # 5. Incoming data
        sections.append(self._format_incoming_data(raw_events))
        
        # 6. Urgency instructions
        sections.append(self.parts.get_urgency_instructions())
        
        if pending_actions and pending_actions.strip():
            sections.append(f"\n## PENDING ACTIONS\n\n{pending_actions}")
        
        if context_parts:
            sections.append(self._format_additional_context(context_parts))
        
        # 7. Grounding rules
        if has_vision:
            sections.append(self.parts.get_vision_grounding())
        sections.append(self.parts.get_grounding_rules())

        # 8. Spoken Response Decision
        sections.append(self.parts.get_spoken_response_rules())
        
        # 9. Output format
        sections.append(self.parts.get_output_format())
        
        # 10. Important reminders (if available) - ALWAYS LAST
        reminders = self.personality.format_important_reminders()
        if reminders:
            sections.append(reminders)
        
        prompt = "\n".join(sections)
        
        if self.logger:
            self.logger.reactive(f"{prompt}")
        
        return prompt
    
    def _format_thought_chain(self, thoughts: List[str]) -> str:
        """Format thoughts for context"""
        if not thoughts:
            return "\n## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
        
        formatted = "\n".join([f"- {t}" for t in thoughts])
        return f"""
## YOUR RECENT THOUGHTS
### SOURCE LABELS
- [THOUGHT] These are your recent thoughts
- [USER] This is the user's input
- [SELF] These are your spoken responses
- [FAMILY] These are the spoken responses from your AI family members
- [SYSTEM]/[TOOL]/etc. These are internal processing messages from your code execution

### YOUR RECENT THOUGHT CHAIN:
{formatted}
"""
    
    def _build_minimal_tool_list(self) -> str:
        """Build minimal tool list (names + 1-line descriptions only)"""
        from BASE.handlers.tool_instruction_builder import ToolInstructionBuilder
        
        builder = ToolInstructionBuilder(
            tool_manager=self.tool_manager,
            logger=self.logger
        )
        
        return builder.build_tool_list_section()
    
    def _format_incoming_data(self, raw_events: List[Any]) -> str:
        """Format incoming events"""
        if not raw_events:
            return "\n## NEW INCOMING DATA\n\nNo new data."
        
        lines = ["\n## NEW INCOMING DATA\n"]
        for i, event in enumerate(raw_events, 1):
            source = getattr(event, 'source', 'unknown')
            data = getattr(event, 'data', str(event))
            lines.append(f"**[Event {i}]** `{source}`: {data}")
        
        return "\n".join(lines)
    
    def _format_additional_context(self, context_parts: List[str]) -> str:
        """Format additional context"""
        formatted = "\n\n".join(context_parts)
        return f"\n## ADDITIONAL CONTEXT\n\n{formatted}"