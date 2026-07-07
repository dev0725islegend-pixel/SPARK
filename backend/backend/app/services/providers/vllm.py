from typing import Any, Dict, Iterable, Tuple, List
import logging
from backend.app.services.providers.generic_http import GenericHTTPProvider

logger = logging.getLogger("model.providers.vllm")

class VLLMAdapter(GenericHTTPProvider):
    """Adapter for vLLM-based HTTP servers. Many vLLM wrappers expose /generate and /stream endpoints.

    Uses GenericHTTPProvider heuristics; override config.endpoints if your vLLM server uses custom paths.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        if "endpoints" not in config:
            config = dict(config)
            config["endpoints"] = {"generate": "/generate", "stream": "/stream", "health": "/health", "models": "/models"}
        super().__init__(name, config)
