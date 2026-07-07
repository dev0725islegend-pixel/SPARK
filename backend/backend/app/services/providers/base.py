from __future__ import annotations
import abc
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

class ProviderAdapter(abc.ABC):
    """Base class for model provider adapters. All providers must implement this interface.

    Methods:
    - generate(prompt, **kwargs) -> dict : Blocking generation returning a structured response
    - stream(prompt, **kwargs) -> Iterable[str] : Streaming generator of token strings
    - health() -> Tuple[bool, dict] : Provider health check
    - list_models() -> List[dict] : List available models or engines
    """

    name: str

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    @abc.abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def health(self) -> Tuple[bool, Dict[str, Any]]:
        raise NotImplementedError()

    @abc.abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        raise NotImplementedError()
