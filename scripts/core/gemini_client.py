
import os
import logging
import json
import time
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Wrapper for Google Gemini API (google-generativeai).
    Handles authentication, model configuration, and structured output parsing.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Gemini features will be disabled.")
            self._model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model_name = model_name
            self._model = genai.GenerativeModel(model_name)
            logger.info(f"Initialized Gemini client with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._model = None

    @property
    def is_available(self) -> bool:
        return self._model is not None

    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """
        Generate text content from the model.
        """
        if not self.is_available:
            return None

        try:
            # Gemini Python SDK doesn't always support 'system_instruction' directly in generate_content depending on version,
            # but usually it's set on model init or passed in config. 
            # For simplicity in this wrapper, we'll prepend system instruction if needed, 
            # or rely on the newer SDK features if available.
            # Let's try to set it via the generation_config or just prepend it to prompt for maximum compatibility.
            
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System Instruction:\n{system_instruction}\n\nUser Request:\n{prompt}"

            response = self._model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2, # Low temp for analytical tasks
                    candidate_count=1
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            if response.text:
                return response.text
            return None

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate and parse JSON output.
        """
        if not self.is_available:
            return None

        # Enforce JSON formatting in prompt if not present
        json_prompt = prompt
        if "return valid JSON" not in prompt.lower() and "json format" not in prompt.lower():
            json_prompt += "\n\nPlease output ONLY valid JSON."

        response_text = self.generate_content(json_prompt, system_instruction)
        
        if not response_text:
            return None

        try:
            # Clean up markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            
            clean_text = clean_text.strip()
            return json.loads(clean_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            return None
