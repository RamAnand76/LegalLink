"""
LLM Service - Handles communication with OpenRouter API.
"""
import requests
import json
import logging
from typing import List, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.site_url = settings.OPENROUTER_SITE_URL
        self.site_name = settings.OPENROUTER_SITE_NAME

    def generate_response(
        self,
        user_message: str,
        context: List[str] = None,
        chat_history: List[Dict[str, str]] = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate a response using OpenRouter API.
        
        Args:
            user_message: The user's current message
            context: Retrieved context from RAG
            chat_history: Previous messages in the conversation
            system_prompt: Custom system prompt (optional)
        
        Returns:
            The AI's response as a string
        """
        if not self.api_key:
            return "Error: OpenRouter API key not configured. Please set OPENROUTER_API_KEY in your environment."

        # Build the system prompt with context
        if system_prompt is None:
            system_prompt = self._build_system_prompt(context)

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history
        if chat_history:
            for msg in chat_history[-10:]:  # Limit to last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.site_name,
                },
                data=json.dumps({
                    "model": self.model,
                    "messages": messages
                }),
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Unexpected API response: {result}")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except requests.exceptions.Timeout:
            logger.error("OpenRouter API timeout")
            return "The request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            return f"An error occurred while communicating with the AI service: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again."

    def _build_system_prompt(self, context: List[str] = None) -> str:
        """Build the system prompt with optional RAG context."""
        base_prompt = """You are LegalLink AI Assistant, a helpful and knowledgeable legal assistant. 
You provide accurate, helpful information about legal topics while being conversational and easy to understand.

Important guidelines:
- Be helpful, accurate, and professional
- If you're unsure about something, say so clearly
- Always recommend consulting with a qualified legal professional for specific legal advice
- Use the provided context to answer questions when available
- If the context doesn't contain relevant information, use your general knowledge but mention this
"""
        
        if context and any(context):
            context_text = "\n\n".join(context)
            base_prompt += f"""

---
RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{context_text}
---

Use the above context to help answer the user's question. If the context is relevant, base your answer on it.
"""
        
        return base_prompt


# Singleton instance
llm_service = LLMService()
