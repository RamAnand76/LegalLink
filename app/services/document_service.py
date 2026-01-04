"""
Document Generation Service - Extracts info from user input and generates legal documents.
"""
import re
import json
import logging
from typing import List, Dict, Optional, Tuple
from app.services.llm_service import llm_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentGeneratorService:
    """Service for generating legal documents from templates and user input."""
    
    def extract_fields_from_input(
        self, 
        user_input: str, 
        required_fields: List[str],
        field_descriptions: Optional[List[dict]] = None
    ) -> Tuple[Dict[str, str], List[dict]]:
        """
        Use LLM to extract required field values from user's natural language input.
        
        Returns:
            Tuple of (extracted_values dict, extraction_details list)
        """
        # Build field description text
        field_info = []
        for field in required_fields:
            desc = ""
            if field_descriptions:
                for fd in field_descriptions:
                    if fd.get("field_name") == field:
                        desc = fd.get("description", "")
                        break
            field_info.append(f"- {field}: {desc}" if desc else f"- {field}")
        
        fields_text = "\n".join(field_info)
        
        extraction_prompt = f"""You are a legal document assistant. Extract the following information from the user's description.

REQUIRED FIELDS TO EXTRACT:
{fields_text}

USER'S DESCRIPTION:
{user_input}

INSTRUCTIONS:
1. Extract values for each required field from the user's description
2. If a value is not found, use "NOT_PROVIDED" as the value
3. Be precise and extract only what is explicitly stated or can be clearly inferred
4. For dates, use format: DD/MM/YYYY
5. For names, use proper capitalization

Respond ONLY with a valid JSON object in this exact format:
{{
    "extracted_fields": [
        {{"field_name": "field1", "value": "extracted value", "confidence": 0.9}},
        {{"field_name": "field2", "value": "extracted value", "confidence": 0.8}}
    ]
}}

JSON Response:"""

        try:
            response = llm_service.generate_response(
                user_message=extraction_prompt,
                context=None,
                chat_history=None,
                system_prompt="You are a precise information extraction assistant. Always respond with valid JSON only."
            )
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                extracted_fields = result.get("extracted_fields", [])
                
                # Convert to dict
                values_dict = {}
                for field in extracted_fields:
                    field_name = field.get("field_name")
                    value = field.get("value", "NOT_PROVIDED")
                    if value != "NOT_PROVIDED":
                        values_dict[field_name] = value
                
                return values_dict, extracted_fields
            else:
                logger.error(f"Could not parse JSON from LLM response: {response}")
                return {}, []
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {}, []
        except Exception as e:
            logger.error(f"Error extracting fields: {e}")
            return {}, []
    
    def fill_template(
        self, 
        template_content: str, 
        field_values: Dict[str, str],
        required_fields: List[str]
    ) -> Tuple[str, List[str]]:
        """
        Fill template placeholders with extracted values.
        
        Returns:
            Tuple of (filled_content, list_of_missing_fields)
        """
        filled_content = template_content
        missing_fields = []
        
        # Find all placeholders in template
        placeholders = re.findall(r'\{\{(\w+)\}\}', template_content)
        
        for placeholder in placeholders:
            if placeholder in field_values:
                filled_content = filled_content.replace(
                    f"{{{{{placeholder}}}}}", 
                    field_values[placeholder]
                )
            else:
                # Mark as missing if it's a required field
                if placeholder in required_fields:
                    missing_fields.append(placeholder)
                # Leave placeholder for non-required fields
                filled_content = filled_content.replace(
                    f"{{{{{placeholder}}}}}", 
                    f"[{placeholder.upper()}]"
                )
        
        return filled_content, missing_fields
    
    def generate_document_from_description(
        self,
        description: str,
        category: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a complete legal document from natural language description.
        Uses LLM to create the document directly.
        
        Returns:
            Dict with 'title', 'content', 'category'
        """
        category_hint = f"Document type: {category}" if category else "Determine the appropriate document type"
        title_hint = f"Title: {title}" if title else "Generate an appropriate title"
        
        generation_prompt = f"""You are an expert legal document drafter. Generate a formal legal document based on the following description.

USER'S DESCRIPTION:
{description}

{category_hint}
{title_hint}

INSTRUCTIONS:
1. Generate a properly formatted legal document
2. Use formal legal language appropriate for Indian courts
3. Include all standard sections (header, parties, facts, prayer, etc.)
4. Fill in details from the description
5. For any missing critical information, use placeholders like [PETITIONER'S ADDRESS]
6. Add appropriate legal citations where relevant

Generate the document in the following format:
---
TITLE: [Document Title]
CATEGORY: [complaint/petition/application/notice/affidavit/agreement/other]
---
[Document Content]
---

Begin generating:"""

        try:
            response = llm_service.generate_response(
                user_message=generation_prompt,
                context=None,
                chat_history=None,
                system_prompt="You are an expert legal document drafter specializing in Indian law. Generate formal, properly structured legal documents."
            )
            
            # Parse the response
            result = {
                "title": title or "Legal Document",
                "content": response,
                "category": category or "other"
            }
            
            # Try to extract title and category from response
            title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', response)
            if title_match:
                result["title"] = title_match.group(1).strip()
            
            category_match = re.search(r'CATEGORY:\s*(.+?)(?:\n|$)', response)
            if category_match:
                extracted_cat = category_match.group(1).strip().lower()
                valid_categories = ["complaint", "petition", "application", "notice", "affidavit", "agreement", "other"]
                if extracted_cat in valid_categories:
                    result["category"] = extracted_cat
            
            # Clean up the content (remove the header section)
            content = response
            if "---" in content:
                parts = content.split("---")
                if len(parts) >= 3:
                    content = "---".join(parts[2:]).strip()
                elif len(parts) >= 2:
                    content = parts[-1].strip()
            
            result["content"] = content if content else response
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return {
                "title": title or "Legal Document",
                "content": f"Error generating document: {str(e)}",
                "category": category or "other"
            }
    
    def suggest_template(self, description: str, available_templates: List[dict]) -> Optional[str]:
        """
        Suggest the best template based on user's description.
        
        Returns:
            Template ID of the best match, or None
        """
        if not available_templates:
            return None
        
        templates_info = "\n".join([
            f"- ID: {t['id']}, Name: {t['name']}, Category: {t['category']}, Description: {t.get('description', 'N/A')}"
            for t in available_templates
        ])
        
        suggestion_prompt = f"""Based on the user's legal matter description, suggest the most appropriate document template.

AVAILABLE TEMPLATES:
{templates_info}

USER'S DESCRIPTION:
{description}

Respond with ONLY the template ID (UUID) of the best matching template, or "NONE" if no template is suitable.

Template ID:"""

        try:
            response = llm_service.generate_response(
                user_message=suggestion_prompt,
                context=None,
                chat_history=None,
                system_prompt="You are a legal document assistant. Respond with only the template ID."
            )
            
            # Extract UUID from response
            uuid_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', response.lower())
            if uuid_match:
                return uuid_match.group()
            
            return None
            
        except Exception as e:
            logger.error(f"Error suggesting template: {e}")
            return None


# Singleton instance
document_generator = DocumentGeneratorService()
