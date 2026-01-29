"""Google Gemini LLM client for AI agent."""
import os
from typing import Optional, Dict, Any
from backend.config import settings

# Use the working package (google.generativeai)
# The new google.genai has different API, keeping old one for compatibility
import google.generativeai as genai


class GeminiClient:
    """Client for using Google Gemini API (free tier)."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Get one at https://makersuite.google.com/app/apikey")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        # Use model from config or default to gemini-2.5-flash
        # Available models: gemini-2.5-flash, gemini-1.5-flash, gemini-1.5-pro
        self.model_name = getattr(settings, 'gemini_model', 'gemini-2.5-flash')
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_output_tokens: int = 8192) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt (Gemini uses it in the prompt)
            max_output_tokens: Maximum tokens in response (default: 8192 for comprehensive answers)
        
        Returns: Generated text
        """
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=max_output_tokens,  # Configurable token limit
                )
            )
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def chat(self, messages: list[Dict[str, str]]) -> str:
        """
        Chat completion using Gemini.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Returns: Assistant response
        """
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Add messages
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "user":
                    chat.send_message(content)
                elif role == "assistant":
                    # Gemini doesn't support assistant messages in history directly
                    # We'll handle this by including in the next user message
                    pass
            
            # Get last response
            response = chat.last.text
            return response
        except Exception as e:
            raise Exception(f"Gemini chat error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.api_key is not None and len(self.api_key) > 0
