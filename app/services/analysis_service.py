"""
Analysis Service - Handles loophole detection and document analysis.
"""
import os
import logging
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class AnalysisService:
    def analyze_document(self, file_path: str, custom_instructions: str = None) -> dict:
        """
        Analyze a document for loopholes and concerns.
        """
        try:
            # Extract text
            text = self._extract_text(file_path)
            if not text:
                return {"error": "Could not extract text from document"}
            
            # Truncate text if too long (LLM context limit)
            # For a real system, we'd need a map-reduce chain or chunking summary strategy
            # Here we'll take the first 15,000 chars as a proof of concept
            truncated_text = text[:15000]
            if len(text) > 15000:
                truncated_text += "\n...[Text truncated due to length]..."
            
            # Build prompt
            prompt = f"""You are an expert legal analyst. Analyze the following legal document contract/agreement for potential loopholes, risks, and dangerous clauses.

DOCUMENT TEXT:
{truncated_text}

CUSTOM INSTRUCTIONS:
{custom_instructions if custom_instructions else "No specific instructions. Perform a general comprehensive risk analysis."}

INSTRUCTIONS:
1. Identify ambiguous clauses that could be exploited.
2. Highlight missing standard protections for the user.
3. Flag any unusually punitive terms.
4. Provide a summary of the document's intent vs. reality.

Format your response as a valid JSON object:
{{
  "analysis": "General summary of the document...",
  "concerns": ["Concern 1", "Concern 2"],
  "loopholes": ["Loophole 1", "Loophole 2"]
}}
"""
            # Generate response
            response = llm_service.generate_response(
                user_message=prompt,
                system_prompt="You are a senior legal risk analyst. detailed and critical. Return JSON only."
            )
            
            # Simple JSON parsing (in production use a robust parser)
            import json
            import re
            
            try:
                # Find JSON blob
                match = re.search(r'\{[\s\S]*\}', response)
                if match:
                    json_str = match.group()
                    result = json.loads(json_str)
                    return result
                else:
                    logger.warning("Could not parse JSON from analysis response")
                    return {
                        "analysis": response,
                        "concerns": [],
                        "loopholes": []
                    }
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                return {
                    "analysis": response,
                    "concerns": [],
                    "loopholes": []
                }
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}

    def _extract_text(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return ""
                
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".pdf":
                try:
                    loader = PyPDFLoader(file_path)
                    pages = loader.load()
                    if not pages:
                        logger.warning(f"No pages loaded from PDF: {file_path}")
                        return ""
                    return "\n".join([p.page_content for p in pages])
                except Exception as e:
                    logger.error(f"PyPDFLoader failed: {e}")
                    # Fallback or re-raise if critical
                    return ""
                    
            elif file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            elif file_ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]:
                # Use Gemini Vision to extract text from images
                try:
                    from google import genai
                    from app.core.config import settings
                    
                    if not settings.GEMINI_API_KEY:
                        logger.warning("GEMINI_API_KEY not set — cannot extract text from images")
                        return ""
                    
                    client = genai.Client(api_key=settings.GEMINI_API_KEY)
                    
                    # Read image bytes
                    with open(file_path, "rb") as img_file:
                        image_bytes = img_file.read()
                    
                    # Determine MIME type
                    mime_map = {
                        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".png": "image/png", ".webp": "image/webp",
                        ".bmp": "image/bmp", ".gif": "image/gif",
                    }
                    mime_type = mime_map.get(file_ext, "image/jpeg")
                    
                    # Send image + prompt to Gemini
                    response = client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=[
                            {
                                "parts": [
                                    {"text": "Extract ALL text from this image exactly as it appears. Return only the extracted text, nothing else."},
                                    {"inline_data": {"mime_type": mime_type, "data": __import__('base64').b64encode(image_bytes).decode('utf-8')}}
                                ]
                            }
                        ]
                    )
                    
                    extracted = response.text.strip() if response.text else ""
                    if extracted:
                        logger.info(f"Gemini Vision extracted {len(extracted)} chars from image")
                    else:
                        logger.warning("Gemini Vision returned empty text for image")
                    return extracted
                    
                except Exception as e:
                    logger.error(f"Gemini Vision extraction failed: {e}")
                    return ""
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

analysis_service = AnalysisService()
