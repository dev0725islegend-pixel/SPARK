"""AI service thin wrapper kept for backward compatibility with existing code.

Refactors previous AIService implementation to use the Model Gateway.
"""
from typing import Generator, Dict, Any
import logging
from backend.app.services.model_gateway import get_model_gateway

logger = logging.getLogger("ai.service")

class AIService:
    def __init__(self):
        self.gateway = get_model_gateway()

    def generate_response(self, prompt: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        logger.info("AIService.generate_response prompt_len=%d", len(prompt))
        return self.gateway.generate(prompt, params=params or {})

    def stream_response(self, prompt: str, params: Dict[str, Any] | None = None) -> Generator[str, None, None]:
        logger.info("AIService.stream_response prompt_len=%d", len(prompt))
        for token in self.gateway.stream(prompt, params=params or {}):
            yield token

    def health_check(self):
        return self.gateway.health()
