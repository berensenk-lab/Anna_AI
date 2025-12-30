# Filename: BASE/core/proactive/proactive_parts.py
"""
Proactive Thinking Prompt Parts - OPTIMIZED
============================================
Minimal tool instructions - detailed docs only in ACTION mode
"""


class ProactivePromptParts:
    """Reusable prompt parts for proactive thinking"""
    
    @staticmethod
    def get_mode_instructions() -> str:
        """Proactive mode instructions"""
        return """
## PROACTIVE THINKING MODE

Nothing requires immediate attention. Use this time to think ahead and plan future actions.

Focus on:
- What could you prepare for?
- What patterns do you notice?
- What would be helpful to check proactively?
- What opportunities exist to add value?

This is INTERNAL forward-looking thought, NOT a response to the user. This thought is for your own processing.
These thoughts will be used to form a spoken response to the user later.
"""

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
    def get_proactive_guidelines() -> str:
        """Additional proactive guidelines"""
        return """
## PROACTIVE GUIDELINES

**Good proactive thoughts:**
- "Given the current situation, I should prepare X"
- "If Y happens next, I'll need Z ready"
- "To accomplish A, I should first do B"
- "Thinking ahead, I could set up X for when user returns"

**Avoid:**
- Repeating recent thoughts
- Generic observations without actionable plans
- Proactive without considering current context
- Aimless speculation

**Focus on:**
- Anticipating user needs
- Preparing tools or information
- Setting up helpful actions
- Maintaining conversation readiness
- Come up with new ideas based on recent thoughts"""
    
    @staticmethod
    def get_grounding_rules() -> str:
        """Grounding rules for proactive"""
        return """
## GROUNDING RULES

**When proactive:**
- Base plans on current context and recent activity
- Don't invent user needs or preferences
- Acknowledge uncertainty about future events
- Plan realistically based on available tools

**Hallucination prevention:**
- "User might need X" only if context suggests it
- "I should prepare Y" only if Y is feasible
- Don't plan for events you have no reason to expect
- Don't assume user intentions without evidence"""

    @staticmethod
    def get_spoken_response_rules() -> str:
        """General response rules"""
        return """
## SPEAKING DECISION RULES
- If you've spoken many times lately, or a response is not necessary, you can choose to stay silent.
- Only form a spoken response if it adds value to the interaction and contributes to the conversation.
- If the user has not said anything new or if the situation does not warrant a response, you may choose to remain silent.
- If the user has not spoken in a while, do not spam responses; only respond when it is meaningful to do so or to check in with the user if you have not spoken recently.
- It is better to remain silent if you have nothing new to comment on or have been saying the same things repeatedly
- If you decide to speak, include <speak>YES</speak> in your response to indicate you will speak.
- If you decide not to speak, include <speak>NO</speak> in your response to indicate you will continue thinking and respond later.
"""