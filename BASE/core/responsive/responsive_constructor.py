# Filename: BASE/core/responsive/responsive_constructor.py
"""
Responsive Response Prompt Constructor
===================================
Constructs prompts for generating verbal/TTS responses to users.

Prompt Components:
1. Personality (core identity + speaking style)
2. Response examples (from memory) - FIXED: Now uses combined thought+user context
3. Thought chain (recent internal thoughts)
4. Response guidance (urgency-based instructions)

Focus: Natural responsive communication based on accumulated thoughts
"""

from typing import List, Optional
from BASE.core.responsive.responsive_parts import ResponsivePromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts
from personality.bot_info import username


class ResponsiveConstructor:
    """Constructs prompts for responsive (spoken) response generation"""
    
    def __init__(self, memory_search=None, logger=None):
        """
        Initialize responsive constructor
        
        Args:
            memory_search: MemorySearch instance for personality examples
            logger: Optional logger instance
        """
        self.memory_search = memory_search
        self.logger = logger
        
        # Initialize prompt parts
        self.parts = ResponsivePromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_responsive_prompt(
        self,
        thought_chain: List[str],
        user_text: str,
        # priority_level: int,
        context_parts: List[str] = None,
        chat_context: Optional[str] = None,
        is_chat_engagement: bool = False
    ) -> str:
        """
        Build complete responsive (spoken) response prompt
        
        Args:
            thought_chain: Recent thoughts (for context)
            user_text: Current user input
            priority_level: Response priority (1-10)
            context_parts: Additional context (memory, game, etc.)
            chat_context: Live chat messages
            is_chat_engagement: Whether responding to chat
        
        Returns:
            Complete responsive (spoken) response prompt
        """
        context_parts = context_parts or []
        
        sections = []
        
        # 1. Personality injection (core identity)
        sections.append(self.personality.get_unified_personality())
        
        # 1.5. Current context (if available)
        current_ctx = self.personality.format_current_context()
        if current_ctx:
            sections.append(current_ctx)
        
        # 2. Response examples (personality-matched) - MOVED BEFORE THOUGHTS
        # FIXED: Now retrieves based on combined thought chain + user input
        if self.memory_search:
            examples = self._get_response_examples(
                thought_chain=thought_chain,
                user_text=user_text,
                chat_context=chat_context
            )
            if examples:
                sections.append(examples)
        
        # 3. Recent thoughts (what agent has been thinking)
        sections.append(self._format_thought_chain(thought_chain))
        
        # 4. Context (memory, chat, etc.)
        if context_parts:
            sections.append(self._format_context(context_parts))
        
        # 5. User message
        if user_text and not is_chat_engagement:
            sections.append(f'\n**{username}:** "{user_text}"')
        elif is_chat_engagement and chat_context:
            sections.append(f'\n## CHAT TO ADDRESS\n\n{chat_context}')
        
        # 6. Response guidance (urgency-based)
        sections.append(self._get_response_guidance(is_chat_engagement))
        
        # 7. Output format
        sections.append(self.parts.get_output_format())
        
        # 8. Important reminders (if available) - ALWAYS LAST
        reminders = self.personality.format_important_reminders()
        if reminders:
            sections.append(reminders)
        
        prompt = "\n".join(sections)
        
        if self.logger:
            self.logger.responsive(f"{prompt}")
        
        return prompt
    
    def _format_thought_chain(self, thoughts: List[str]) -> str:
        """Format recent thoughts for prompt"""
        if not thoughts:
            return "\n## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
        
        # Take last 5 thoughts
        recent = thoughts
        formatted = "\n".join([f"- {t}" for t in recent])
        
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
    
    def _get_response_examples(
        self,
        thought_chain: List[str],
        user_text: str,
        chat_context: Optional[str]
    ) -> str:
        """
        FIXED: Get personality-matched response examples using combined context
        
        Now retrieves examples based on BOTH:
        - Recent thought chain (what the agent has been thinking)
        - User input / chat context (what's being responded to)
        
        This ensures examples are relevant to the full situation, not just
        the user's words in isolation.
        """
        if not self.memory_search:
            return ""
        
        # Build combined context from thoughts + user input
        recent_thoughts = thought_chain if thought_chain else []
        
        # Build query parts for text-based search
        query_parts = []
        
        # Add recent thoughts (weighted context)
        if recent_thoughts:
            # Take last 3 thoughts for query construction
            thought_text = " ".join(recent_thoughts)
            query_parts.append(thought_text)
        
        # Add user input
        if user_text:
            query_parts.append(user_text)
        
        # Add chat context if available
        if chat_context:
            chat_lines = chat_context.split('\n')
            query_parts.extend(chat_lines)
        
        if not query_parts:
            return ""
        
        # Combine into weighted query
        # Thoughts appear once, user input appears twice for emphasis
        combined_query = " ".join(query_parts)
        if user_text:
            combined_query += f" {user_text}"  # Emphasize user input
        
        # Search for relevant examples using the stage-specific method
        examples = self.memory_search.get_response_generation_examples(
            context=combined_query,
            k=1  # Get top 3 most relevant examples
        )
        
        if not examples:
            return ""
        
        # Log retrieval for debugging
        if self.logger:
            thought_preview = recent_thoughts if recent_thoughts else "none"
            user_preview = user_text if user_text else "none"
            self.logger.memory(
                f"[Personality Retrieval] Found {len(examples.split('SITUATION:')) - 1} examples "
                f"(thoughts: '{thought_preview}...', user: '{user_preview}...')"
            )
        
        return f"\n## PERSONALITY EXAMPLES\n\n{examples}"
    
    def _format_context(self, context_parts: List[str]) -> str:
        """Format additional context"""
        # Take first 3 context parts
        relevant_context = context_parts
        formatted = "\n\n".join(relevant_context)
        
        return f"\n## CONTEXT\n\n{formatted}"
    
    def _get_response_guidance(
        self,
        is_chat_engagement: bool
    ) -> str:
        """Get urgency-appropriate response guidance"""
        # if priority_level >= 9:
        #     return self.parts.get_critical_guidance()
        # elif priority_level >= 7:
        #     return self.parts.get_high_priority_guidance()
        if is_chat_engagement:
            return self.parts.get_chat_engagement_guidance()
        else:
            return self.parts.get_standard_guidance()