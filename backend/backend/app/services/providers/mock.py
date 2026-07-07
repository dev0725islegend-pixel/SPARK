from typing import Any, Dict, Iterable, Tuple, List
import logging
from backend.app.services.providers.base import ProviderAdapter

logger = logging.getLogger("model.providers.mock")

class MockAdapter(ProviderAdapter):
    """A minimal, configurable in-process mock adapter used only for internal tests.
    It is NOT added to docker-compose by default. It returns simple deterministic results.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config or {})

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return {"id": "mock-1", "object": "mocked_response", "text": f"Echo: {prompt}", "meta": {}}

    def stream(self, prompt: str, **kwargs) -> Iterable[str]:
        # naive tokenization by words
        for w in (prompt + "").split():
            yield w + " "

    def health(self) -> Tuple[bool, Dict[str, Any]]:
        return True, {"provider": "mock", "status": "ok"}

    def list_models(self) -> List[Dict[str, Any]]:
        return [{"name": "mock-small", "id": "mock-small"}]
