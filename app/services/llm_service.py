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
        elif self.provider == "gemini":
            self.api_key = settings.GEMINI_API_KEY
            self.model = settings.GEMINI_MODEL
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
        Generate a response using the configured LLM provider with fallback rotation.
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

        if self.provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                
                # Combine prompt for gemini
                full_prompt = f"System: {system_prompt}\n\n"
                if chat_history:
                    for msg in chat_history[-10:]:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        full_prompt += f"{role}: {msg['content']}\n\n"
                full_prompt += f"User: {user_message}"
                
                response = client.models.generate_content(
                    model=self.model,
                    contents=full_prompt
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini generation failed: {e}")
                return f"I couldn't generate a response. The service is currently busy or experiencing issues. (Last error: {e})"

        # Prepare headers based on provider
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = self.site_url
            headers["X-Title"] = self.site_name
        
        # Prepare list of models to try (primary + fallbacks)
        models_to_try = [self.model]
        if self.provider == "openrouter" and settings.ENABLE_MODEL_FALLBACK:
            models_to_try.extend(settings.OPENROUTER_FALLBACK_MODELS)
            
        last_error = None
        
        for model in models_to_try:
            payload = {
                "model": model,
                "messages": messages,
            }
            
            try:
                logger.info(f"Attempting generation with model: {model}")
                response = requests.post(
                    url=self.api_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=60,
                )
                
                # If successful, return immediately
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0]["message"]["content"]
                            if model != self.model:
                                logger.info(f"Switched primary model to {model} after successful fallback")
                            return content
                        elif "error" in result:
                            # API returned 200 but with error in body (rare but possible)
                            logger.warning(f"API returned error in body for {model}: {result['error']}")
                            last_error = f"API Error: {result['error']}"
                            continue # Try next model
                    except ValueError:
                        logger.error(f"Failed to decode JSON response from {model}")
                        last_error = "Invalid JSON response"
                        continue

                # Handle HTTP errors
                # We retry on:
                # 429: Rate Limit
                # >= 500: Server Error
                # 404: Model not found/unavailable
                # 402: Payment Required (maybe quota exceeded, try free model)
                # 400: Bad Request (could be context length, trying another model might work)
                if response.status_code in [429, 402, 404] or response.status_code >= 500 or response.status_code == 400:
                    logger.warning(f"Request failed ({response.status_code}) for model {model}. trying next... Response: {response.text[:200]}")
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    continue
                
                # 401 is Unauthorized (Invalid API Key) - Retrying won't help if using same key
                if response.status_code == 401:
                     logger.error(f"Invalid API Key ({response.status_code}) for model {model}.")
                     last_error = "Invalid API Key"
                     break
                     
                # Other client errors
                logger.error(f"Client error ({response.status_code}) for model {model}: {response.text}")
                last_error = f"Error {response.status_code}: {response.text}"
                continue # Let's retry anyway just in case it's model-specific
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request connection failed for model {model}: {e}. Trying next...")
                last_error = str(e)
                continue
            except Exception as e:
                logger.error(f"Unexpected error for model {model}: {e}. Trying next...")
                last_error = str(e)
                continue
                
        # If we get here, all models failed
        logger.error("All available models failed.")
        
        # Try OpenAI fallback as a last resort if configured and different from above
        if self.provider == "openrouter" and settings.OPENAI_API_KEY:
            logger.info("Falling back to OpenAI as last resort.")
            try:
                openai_headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
                openai_payload = {"model": settings.OPENAI_MODEL, "messages": messages}
                
                response = requests.post(
                    url="https://api.openai.com/v1/chat/completions", 
                    headers=openai_headers, 
                    data=json.dumps(openai_payload), 
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"OpenAI fallback also failed: {e}")
                
        return f"I couldn't generate a response. The service is currently busy or experiencing issues. (Last error: {last_error})"

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
