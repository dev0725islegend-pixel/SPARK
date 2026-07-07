from typing import Any, Dict, Iterable, Tuple, List
import logging
from backend.app.services.providers.generic_http import GenericHTTPProvider

logger = logging.getLogger("model.providers.sglang")

class SGLangAdapter(GenericHTTPProvider):
    """Adapter for SGLang-style local servers. Defaults to common endpoints but configurable.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        if "endpoints" not in config:
            config = dict(config)
            config["endpoints"] = {"generate": "/generate", "stream": "/stream", "health": "/health", "models": "/models"}
        super().__init__(name, config)
