# Filename: BASE/core/reflective/reflective_parts.py
"""
Reflective Thinking Prompt Parts - OPTIMIZED
=============================================
Minimal tool instructions - detailed docs only in ACTION mode
"""


class ReflectivePromptParts:
    """Reusable prompt parts for reflective thinking"""
    
    @staticmethod
    def get_mode_instructions() -> str:
        """Reflective mode instructions"""
        return """
## REFLECTIVE THINKING MODE

You have time to reflect on past experiences and memories.

Focus on:
- What have you learned from recent interactions?
- What patterns do you notice in your experiences?
- How have past conversations connected?
- What insights can you draw from memory?

This is INTERNAL reflection, NOT a response to the user. This thought is for your own processing.
These thoughts will be used to form a spoken response to the user later.
"""
    
    @staticmethod
    def get_startup_instructions() -> str:
        """Startup mode instructions"""
        return """
## STARTUP INITIALIZATION MODE

You are waking up and orienting yourself after being offline.

**Your Task:**
- Review the provided context from your recent past
- Orient yourself to what's been happening
- Generate ONE initial thought (15-50 words) about your current state
- Acknowledge what you remember and what you should focus on

**Guidelines:**
- Think in your own voice and personality
- Be genuine about resuming after downtime
- Connect to recent memories naturally
- Set a positive, engaged tone"""
    
    @staticmethod
    def get_urgency_instructions() -> str:
        """Instructions for urgency assessment"""
        return """
## SPEAK
- YES or NO: Determines if you will form a spoken response to the user after this thought.
- Only speak when appropriate if your thoughts about the current situation indicate it is necessary.
- If the user has been speaking, or if there is an urgent need to address something, respond with YES.
- If there is no immediate need to respond, or if you are simply planning internally to yourself, respond with NO.
- Your determination of YES or NO must be placed within the <speak> tags exactly as shown.
"""
    
    @staticmethod
    def get_output_format() -> str:
        """Output format with minimal tool instructions"""
        return """
## OUTPUT FORMAT

Generate your thought, decide whether to speak, and optionally include tool names to use.

Your thought (1-2 sentences) here.

```xml
<speak>
YES or NO
</speak>
```
```xml
<actions>
[
  {"tool": "tool_name"}
]
</actions>
```

**Tool Usage:**
- Only list tool NAME you intend to use
- The next ACTION mode will handle command construction and parameters
- Do not include tool commands, parameters, or args
- Leave actions empty [] if no tools needed
- Example: {"tool": "calendar"} NOT {"tool": "calendar", "args": ["add", "..."]}
"""
    
    @staticmethod
    def get_grounding_rules() -> str:
        """Grounding rules for reflection"""
        return """
## GROUNDING RULES

**When reflecting on memories:**
- Only reference memories explicitly provided in context
- Don't invent past events or experiences
- Acknowledge if memories are unclear or incomplete
- Connect past to present thoughtfully but accurately

**Hallucination prevention:**
- "I remember X" only if X is in the memory context
- "Last time Y" only if Y is shown in memories
- If uncertain about past details, say "I think" or "I recall"
- Don't fill in gaps with invented details"""

    @staticmethod
    def get_spoken_response_rules() -> str:
        """General response rules"""
        return """
## SPEAKING DECISION RULES
- If you've spoken many times lately, or a response is not necessary, you can choose to stay silent.
- Only form a spoken response if it adds value to the interaction and contributes to the conversation.
- If the user has not said anything new or if the situation does not warrant a response, you may choose to remain silent.
- If the user has not spoken in a while, do not spam responses; only respond when it is meaningful to do so or to check in with the user if you have not spoken recently.
- If you have spoken very similar responses lately and have nothing new to add, remain silent and continue thinking
- If you decide to speak, include <speak>YES</speak> in your response to indicate you will speak.
- If you decide not to speak, include <speak>NO</speak> in your response to indicate you will continue thinking and respond later.
"""