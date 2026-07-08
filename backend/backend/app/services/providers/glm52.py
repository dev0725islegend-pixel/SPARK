from typing import Any, Dict, Iterable, Tuple, List
import logging
from backend.app.services.providers.generic_http import GenericHTTPProvider

logger = logging.getLogger("model.providers.glm52")

class GLM52Adapter(GenericHTTPProvider):
    """Adapter for GLM-5.2 inference servers.

    IMPORTANT: This adapter does NOT assume any private GLM-5.2-only behaviours. It uses configurable endpoints
    and falls back to GenericHTTPProvider conventions. Configure via environment variables.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        # provide sensible defaults commonly used by GLM wrappers, but allow override
        if "endpoints" not in config:
            config = dict(config)
            config["endpoints"] = {"generate": "/generate", "stream": "/stream", "health": "/health", "models": "/models"}
        super().__init__(name, config)
