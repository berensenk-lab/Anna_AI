# Filename: BASE/core/proactive/proactive_constructor.py
"""
Proactive Thinking Prompt Constructor - OPTIMIZED
==================================================
Minimal tool instructions in cognitive modes - detailed docs only in ACTION mode

Prompt Components:
1. Personality (core identity + proactive style)
2. Thought chain (recent thoughts for continuity)
3. Available tool list (minimal overview only)
4. Current situation (what's happening now)
5. Response guidance (how to plan ahead)

Focus: Looking forward, anticipating needs, setting goals
Tool execution: Handled by separate ACTION mode
"""

from typing import List, Optional
from BASE.core.proactive.proactive_parts import ProactivePromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts
from personality.bot_info import username


class ProactiveConstructor:
    """Constructs prompts for proactive thinking"""

    __slots__ = ('tool_manager', 'logger', 'parts', 'personality')
    
    def __init__(self, tool_manager=None, logger=None):
        self.tool_manager = tool_manager
        self.logger = logger
        self.parts = ProactivePromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_proactive_prompt(
        self,
        thought_chain: List[str],
        ongoing_context: str,
        time_context: Optional[str] = None
    ) -> str:
        """Build complete proactive thinking prompt"""
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
        
        # 5. Current situation
        sections.append(self._format_current_situation(ongoing_context, time_context))

        # 6. Urgency instructions
        sections.append(self.parts.get_urgency_instructions())

        # 7. Spoken Response Decision
        sections.append(self.parts.get_spoken_response_rules())
        
        # 8. Output format
        sections.append(self.parts.get_output_format())
        
        # 9. Important reminders (if available) - ALWAYS LAST
        reminders = self.personality.format_important_reminders()
        if reminders:
            sections.append(reminders)
        
        prompt = "\n".join(sections)
        
        if self.logger:
            log_full = bool(
                getattr(getattr(self.logger, 'config', None), 'LOG_FULL_PROMPTS', False)
            )
            if log_full:
                self.logger.proactive(prompt)
            else:
                self.logger.proactive(f"[Proactive Prompt] length={len(prompt)} chars")
        
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
    
    def _format_current_situation(
        self,
        ongoing_context: str,
        time_context: Optional[str]
    ) -> str:
        """Format current situation and time context"""
        sections = []
        
        sections.append("## CURRENT SITUATION\n")
        sections.append(ongoing_context if ongoing_context else "Open time for proactive")
        
        if time_context:
            sections.append("\n## TIME CONTEXT\n")
            sections.append(time_context)
        elif ongoing_context == "Open time for proactive":
            sections.append("\n## TIME CONTEXT\n")
            sections.append(f"{username} is not currently active. Good time to plan ahead.")
        
        return "\n".join(sections)
