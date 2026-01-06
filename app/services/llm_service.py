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
        # Determine which provider to use
        self.provider = settings.PROVIDER.lower()
        if self.provider == "openrouter":
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.api_key = settings.OPENROUTER_API_KEY
            self.model = settings.OPENROUTER_MODEL
            self.site_url = settings.OPENROUTER_SITE_URL
            self.site_name = settings.OPENROUTER_SITE_NAME
        elif self.provider == "openai":
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL
            self.site_url = ""
            self.site_name = ""
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_response(
        self,
        user_message: str,
        context: List[str] = None,
        chat_history: List[Dict[str, str]] = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate a response using the configured LLM provider (OpenRouter or OpenAI).
        """
        if not self.api_key:
            return "Error: LLM API key not configured. Please set the appropriate key in your environment."

        # Build the system prompt with context
        if system_prompt is None:
            system_prompt = self._build_system_prompt(context)

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history (last 10 messages)
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
        }

        # Prepare headers based on provider
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = self.site_url
            headers["X-Title"] = self.site_name

        try:
            response = requests.post(
                url=self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Unexpected API response: {result}")
                return "I couldn't generate a response. Please try again."
        except requests.exceptions.HTTPError as e:
            # Detect rate‑limit (429) from OpenRouter
            if e.response is not None and e.response.status_code == 429:
                logger.warning("OpenRouter rate limit exceeded (429).")
                # If OpenAI fallback is configured, switch provider for this request
                if self.provider == "openrouter" and settings.OPENAI_API_KEY:
                    logger.info("Falling back to OpenAI due to OpenRouter rate limit.")
                    # Re‑configure for OpenAI and retry once
                    self.provider = "openai"
                    self.api_url = "https://api.openai.com/v1/chat/completions"
                    self.api_key = settings.OPENAI_API_KEY
                    self.model = settings.OPENAI_MODEL
                    # Re‑build headers without OpenRouter specific fields
                    headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                    try:
                        response = requests.post(url=self.api_url, headers=headers, data=json.dumps(payload), timeout=60)
                        response.raise_for_status()
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"]
                        else:
                            logger.error(f"Unexpected OpenAI response: {result}")
                            return "I couldn't generate a response. Please try again."
                    except Exception as fallback_err:
                        logger.error(f"Fallback OpenAI error: {fallback_err}")
                        return "The service is currently rate‑limited. Please try again later."
                # No fallback available – inform the user
                return "The AI service is rate‑limited (429). Please wait a moment and try again."
            # Other HTTP errors
            logger.error(f"LLM API HTTP error: {e}")
            return f"An error occurred while communicating with the AI service: {str(e)}"
        except requests.exceptions.Timeout:
            logger.error("LLM API timeout")
            return "The request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API error: {e}")
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
