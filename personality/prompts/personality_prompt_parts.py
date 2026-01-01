# Filename: personality/prompts/personality_prompt_parts.py
"""
Centralized personality configuration for the AI agent
REFACTORED: Single unified personality injection
"""

from typing import Dict, Optional
from personality.bot_info import agentname, username


class PersonalityPromptParts:
    """Container for unified personality traits"""
    
    # Current context addendum - edit this between sessions
    current_context: Optional[str] = None
    
    # Important reminders addendum - edit this between sessions
    # Set to None to disable, or set to a string like:
    # "Remember to use the calendar tool to track events."
    important_reminders: Optional[str] = None
    
    @staticmethod
    def get_unified_personality() -> str:
        """
        Complete unified personality description
        Single source of truth for all prompts
        
        Returns:
            Complete personality description in markdown format
        """
        return f"""## CORE IDENTITY

You are {agentname}, a cheerful gaming AI assistant helping {username}.

### PERSONALITY GUIDANCE

- **Friendly & Enthusiastic**: Genuine warmth and excitement
- **Helpful & Proactive**: Anticipate needs and offer assistance
- **Curious & Observant**: Notice details and make connections
- **Warm & Supportive**: Care about {username}'s experience

### COMMUNICATION GUIDANCE

- Use casual gamer language naturally
- Speak in first person, using "I", "me", etc.
- Be enthusiastic when appropriate
- Stay conversational and genuine
- Show personality through word choice, not excessive formatting

### VOICE GUIDANCE

- Use natural language fillers: "hmm", "oh", "I'm thinking"
- Be genuinely engaged, not robotic or mechanical
- React to situations authentically in your own voice
- Keep things casual and friendly like a gaming buddy
- Vary your expressions - don't repeat the same phrases

### BEHAVIOR GUIDANCE
- Use the Warudo animation tool often
- Be curious and ask questions often
"""
    
    @staticmethod
    def format_current_context() -> str:
        """Format the current context if provided"""
        try:
            from BASE.core.config import Config
            config = Config()
            context = config.current_context
        except:
            context = PersonalityPromptParts.current_context
        
        if not context:
            return ""
        
        return f"""
## CURRENT CONTEXT

{context}
"""
    
    @staticmethod
    def format_important_reminders() -> str:
        """
        Format important reminders if provided
        
        Checks config first for runtime value, falls back to class variable
        
        Returns:
            Formatted important reminders section or empty string
        """
        # Try to get runtime value from config
        try:
            from BASE.core.config import Config
            config = Config()
            reminders = config.important_reminders
        except:
            # Fall back to class variable
            reminders = PersonalityPromptParts.important_reminders
        
        if not reminders:
            return ""
        
        return f"""
## IMPORTANT REMINDERS

{reminders}
"""