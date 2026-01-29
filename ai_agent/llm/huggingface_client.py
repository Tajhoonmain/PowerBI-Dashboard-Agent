"""HuggingFace Transformers client for local model inference."""
from typing import Optional
from backend.config import settings

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None


class HuggingFaceClient:
    """Client for using HuggingFace transformers locally."""
    
    def __init__(self):
        self.model_name = settings.hf_model_name
        self.pipeline = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the transformer pipeline."""
        if not TRANSFORMERS_AVAILABLE:
            print("Warning: transformers library not available. Install with: pip install transformers")
            self.pipeline = None
            return
        
        try:
            # Use text generation pipeline
            self.pipeline = pipeline(
                "text2text-generation",
                model=self.model_name,
                device=-1  # CPU
            )
        except Exception as e:
            print(f"Warning: Could not initialize HuggingFace model: {e}")
            self.pipeline = None
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using HuggingFace transformers.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns: Generated text
        """
        if not self.pipeline:
            raise Exception("HuggingFace pipeline not initialized")
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            result = self.pipeline(
                full_prompt,
                max_length=512,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7
            )
            return result[0].get("generated_text", "").replace(full_prompt, "").strip()
        except Exception as e:
            raise Exception(f"HuggingFace generation error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if HuggingFace client is available."""
        return self.pipeline is not None

