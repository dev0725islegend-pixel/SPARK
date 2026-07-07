from typing import Any, Dict, Iterable, Tuple, List
import logging
from backend.app.services.providers.generic_http import GenericHTTPProvider

logger = logging.getLogger("model.providers.ollama")

class OllamaAdapter(GenericHTTPProvider):
    """Adapter for Ollama-like local servers.

    Ollama's local HTTP API often exposes endpoints like /api/generate and streaming endpoints.
    This adapter uses GenericHTTPProvider but allows provider-specific defaults.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        # normalize endpoints if not provided
        if "endpoints" not in config:
            config = dict(config)
            config["endpoints"] = {"generate": "/api/generate", "stream": "/api/stream", "health": "/api/health", "models": "/api/models"}
        super().__init__(name, config)
