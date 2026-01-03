# Filename: BASE/core/responsive/responsive_parts.py
"""
Responsive Response Prompt Parts
=============================
Contains reusable prompt components for responsive (spoken) response generation
"""

from personality.bot_info import username


class ResponsivePromptParts:
    """Reusable prompt parts for responsive (spoken) responses"""

    __slots__ = ()  # Static methods only, no instance variables
    
    @staticmethod
    def get_output_format() -> str:
        """Output format instructions"""
        return """
## RESPOND

Respond naturally in 1-2 sentences, no more than 15 words total. Just write your response directly - no XML tags needed.

**Rules:**
- Maximum 1-2 sentences, no more than 15 words total
- Natural conversational tone
- No labels, timestamps, or meta-text
- Form a spoken response based on your recent thoughts"""
    
    @staticmethod
    def get_chat_engagement_guidance() -> str:
        """Guidance for chat engagement responses"""
        return """
## LIVE CHAT ENGAGEMENT

**You are responding via spoken TTS to the live chat.**

Guidelines:
- Address chat members by name when appropriate
- Keep responses conversational and friendly
- You can address up to 2 people in one response
- Sound natural - this will be spoken aloud
- 1-2 sentences maximum, no more than 15 words total"""
    
    @staticmethod
    def get_standard_guidance() -> str:
        """Guidance for standard responses"""
        return """
## RESPONSE GUIDANCE

Respond naturally based on your recent thoughts and the current situation. This is a casual conversation.

Guidelines:
- Respond in 1-2 sentences, no more than 15 words.
- Speak naturally in your own voice
- Keep it conversational and light
- Don't repeat what you just said recently. Responses should not be too similar.
- If your thoughts have been repetitive, mention some future ideas, plans, or goals based on your personality.
- If you are unsure what to say, say something profound or ask a question based on recent context.
- Base your response on your thoughts, personality, and available context

Remember:
- You have decided to speak based on recent thoughts and current context. Form a new spoken statement or question that drives the conversation forward and elicits reaction from the user."""
    
    @staticmethod
    def get_response_rules() -> str:
        """General response rules"""
        return """
## RESPONSE RULES

**Style:**
- Speak naturally and conversationally
- Use your personality and voice
- Keep responses concise (1-2 sentences), no more than 15 words total.
- No emojis, no labels, no meta-text

**Content:**
- Base responses on your recent thoughts
- Don't repeat yourself
- Don't invent information
- Acknowledge uncertainty if needed"""

