from typing import Any, Dict, Iterable, Tuple, List, Optional
import os
import logging
from backend.app.services.providers.base import ProviderAdapter
from backend.app.services.providers.openai import OpenAIAdapter
from backend.app.services.providers.generic_http import GenericHTTPProvider
from backend.app.services.providers.glm52 import GLM52Adapter
from backend.app.services.providers.ollama import OllamaAdapter
from backend.app.services.providers.vllm import VLLMAdapter
from backend.app.services.providers.sglang import SGLangAdapter
from backend.app.services.providers.mock import MockAdapter
from backend.app.core.config import settings

logger = logging.getLogger("model.gateway")

_PROVIDER_REGISTRY = {
    "openai": OpenAIAdapter,
    "generic": GenericHTTPProvider,
    "glm52": GLM52Adapter,
    "ollama": OllamaAdapter,
    "vllm": VLLMAdapter,
    "sglang": SGLangAdapter,
    "mock": MockAdapter,
}


class ModelGateway:
    """A provider-agnostic gateway that centralizes all model access.

    Selection is driven by environment variables (settings):
    - MODEL_PROVIDER: primary provider key (e.g., glm52, openai)
    - MODEL_PROVIDER_FALLBACKS: comma-separated provider keys used for failover
    - PROVIDER_<NAME>_API_URL (or generic MODEL_API_URL) : provider-specific base URL
    - PROVIDER_<NAME>_API_KEY : optional provider API key
    - PROVIDER_<NAME>_MODEL : optional model name

    The gateway instantiates a provider adapter and exposes uniform methods:
    - generate(prompt, **kwargs)
    - stream(prompt, **kwargs)
    - health()
    - list_models()

    The gateway logs requests, responses, latencies, and provider metadata.
    """

    def __init__(self, provider_name: Optional[str] = None):
        self.provider_name = provider_name or settings.MODEL_PROVIDER
        self.fallbacks = [p.strip() for p in (os.environ.get("MODEL_PROVIDER_FALLBACKS") or "").split(",") if p.strip()]
        self._provider = self._load_provider(self.provider_name)

    def _provider_config(self, key: str) -> Dict[str, Any]:
        """Build provider config from environment variables.

        Lookup sequence (most specific -> least):
        - PROVIDER_{KEY}_API_URL
        - PROVIDER_{KEY}_API_KEY
        - PROVIDER_{KEY}_MODEL
        - MODEL_API_URL
        - MODEL_API_KEY
        - MODEL_NAME
        """
        env = os.environ
        cfg = {}
        specific_prefix = f"PROVIDER_{key.upper()}_"
        if env.get(specific_prefix + "API_URL"):
            cfg["api_url"] = env.get(specific_prefix + "API_URL")
        elif env.get("MODEL_API_URL"):
            cfg["api_url"] = env.get("MODEL_API_URL")
        if env.get(specific_prefix + "API_KEY"):
            cfg["api_key"] = env.get(specific_prefix + "API_KEY")
        elif env.get("MODEL_API_KEY"):
            cfg["api_key"] = env.get("MODEL_API_KEY")
        if env.get(specific_prefix + "MODEL"):
            cfg["model"] = env.get(specific_prefix + "MODEL")
        elif env.get("MODEL_NAME"):
            cfg["model"] = env.get("MODEL_NAME")
        # optional endpoints override
        endpoints_raw = env.get(specific_prefix + "ENDPOINTS")
        if endpoints_raw:
            # expected format: generate:/g,stream:/s,health:/h
            endpoints = {}
            for part in endpoints_raw.split(','):
                if ':' in part:
                    k, v = part.split(':', 1)
                    endpoints[k.strip()] = v.strip()
            if endpoints:
                cfg['endpoints'] = endpoints
        # timeout / retries
        if env.get(specific_prefix + "TIMEOUT"):
            cfg['timeout'] = int(env.get(specific_prefix + "TIMEOUT"))
        if env.get(specific_prefix + "MAX_RETRIES"):
            cfg['max_retries'] = int(env.get(specific_prefix + "MAX_RETRIES"))
        return cfg

    def _load_provider(self, key: str) -> ProviderAdapter:
        if not key:
            raise RuntimeError("No MODEL_PROVIDER configured")
        key = key.lower()
        adapter_cls = _PROVIDER_REGISTRY.get(key)
        if not adapter_cls:
            # fallback to generic if unknown
            adapter_cls = GenericHTTPProvider
        cfg = self._provider_config(key)
        provider = adapter_cls(key, cfg)
        logger.info("Loaded model provider '%s' with config keys: %s", key, list(cfg.keys()))
        return provider

    def _failover_load(self) -> None:
        """Try fallbacks in order and set the provider to the first healthy one.
        This is only called when health checks fail for the active provider.
        """
        for fb in self.fallbacks:
            try:
                p = self._load_provider(fb)
                ok, info = p.health()
                if ok:
                    logger.warning("Failing over to provider '%s'", fb)
                    self._provider = p
                    return
            except Exception:
                logger.exception("Failover provider '%s' failed to initialize", fb)
        logger.error("No healthy providers available during failover")

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        logger.info("ModelGateway.generate provider=%s prompt_len=%d", self._provider.name, len(prompt))
        start = time_ns()
        try:
            res = self._provider.generate(prompt, **kwargs)
            elapsed = time_ns() - start
            logger.info("ModelGateway.generate done provider=%s elapsed_ns=%d", self._provider.name, elapsed)
            return res
        except Exception as e:
            logger.exception("ModelGateway.generate error: %s", e)
            # attempt failover
            try:
                self._failover_load()
                res = self._provider.generate(prompt, **kwargs)
                return res
            except Exception:
                raise

    def stream(self, prompt: str, **kwargs) -> Iterable[str]:
        logger.info("ModelGateway.stream provider=%s prompt_len=%d", self._provider.name, len(prompt))
        start = time_ns()
        try:
            for chunk in self._provider.stream(prompt, **kwargs):
                logger.debug("ModelGateway.stream chunk provider=%s chunk_len=%d", self._provider.name, len(chunk))
                yield chunk
        except Exception as e:
            logger.exception("ModelGateway.stream error: %s", e)
            # try failover and re-stream once
            try:
                self._failover_load()
                for chunk in self._provider.stream(prompt, **kwargs):
                    yield chunk
            except Exception:
                raise
        finally:
            elapsed = time_ns() - start
            logger.info("ModelGateway.stream finished provider=%s elapsed_ns=%d", self._provider.name, elapsed)

    def health(self) -> Tuple[bool, Dict[str, Any]]:
        try:
            ok, info = self._provider.health()
            if not ok:
                logger.warning("Provider health check failed for %s: %s", self._provider.name, info)
                # try fallbacks
                self._failover_load()
            return ok, info
        except Exception as e:
            logger.exception("ModelGateway.health error: %s", e)
            self._failover_load()
            return False, {"error": str(e)}

    def list_models(self) -> List[Dict[str, Any]]:
        try:
            return self._provider.list_models()
        except Exception as e:
            logger.exception("ModelGateway.list_models error: %s", e)
            return []


# helpers
def time_ns():
    try:
        import time as _time
        return int(_time.time() * 1e9)
    except Exception:
        return 0

# Provide a module-level singleton for easy importing
_gateway_singleton: Optional[ModelGateway] = None

def get_model_gateway() -> ModelGateway:
    global _gateway_singleton
    if _gateway_singleton is None:
        _gateway_singleton = ModelGateway()
    return _gateway_singleton
