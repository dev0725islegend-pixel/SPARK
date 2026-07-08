from typing import Any, Dict, Iterable, Tuple, List
import httpx
import time
import logging
from backend.app.services.providers.base import ProviderAdapter

logger = logging.getLogger("model.providers.generic")

class GenericHTTPProvider(ProviderAdapter):
    """Provider adapter for HTTP-forwarding model servers.

    This adapter attempts to call common endpoints on the configured provider:
    - POST {api_url}/generate  -> blocking JSON response
    - POST {api_url}/stream    -> streaming response (newline-delimited tokens or JSON lines)
    - GET  {api_url}/health    -> health JSON

    None of these endpoints are strictly required; the adapter will try the best available.
    Configure endpoints via config dict: {"api_url": "http://...", "endpoints": {"generate":"/generate",...}}
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.api_url = config.get("api_url", "")
        self.endpoints = config.get("endpoints", {"generate": "/generate", "stream": "/stream", "health": "/health", "models": "/models"})
        self.timeout = config.get("timeout", 60)
        self.max_retries = int(config.get("max_retries", 3))
        self.headers = config.get("headers", {})

    def _url(self, key: str) -> str:
        path = self.endpoints.get(key)
        if not path:
            raise ValueError(f"No endpoint configured for '{key}'")
        return f"{self.api_url.rstrip('/')}/{path.lstrip('/')}"

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        url = self._url("generate")
        payload = {"prompt": prompt}
        payload.update(kwargs.get("params") or {})
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    r = client.post(url, json=payload, headers=self.headers)
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                logger.exception("GenericHTTPProvider.generate failed (attempt=%s) %s", attempt + 1, e)
                if attempt + 1 >= self.max_retries:
                    raise
                time.sleep(2 ** attempt)

    def stream(self, prompt: str, **kwargs) -> Iterable[str]:
        url = self._url("stream")
        payload = {"prompt": prompt}
        payload.update(kwargs.get("params") or {})
        for attempt in range(self.max_retries):
            try:
                with httpx.stream("POST", url, json=payload, timeout=self.timeout, headers=self.headers) as resp:
                    resp.raise_for_status()
                    for raw in resp.iter_bytes(chunk_size=1024):
                        if not raw:
                            continue
                        text = raw.decode(errors="ignore")
                        parts = text.splitlines()
                        for p in parts:
                            p = p.strip()
                            if not p:
                                continue
                            # try JSON line
                            try:
                                import json
                                j = json.loads(p)
                                # heuristics: token fields
                                if isinstance(j, dict):
                                    for k in ("token", "text", "delta"):
                                        if k in j:
                                            yield j[k]
                                            break
                                    else:
                                        # fallback to entire json string
                                        yield p
                                else:
                                    yield p
                            except Exception:
                                yield p
                    return
            except Exception as e:
                logger.exception("GenericHTTPProvider.stream failed (attempt=%s): %s", attempt + 1, e)
                if attempt + 1 >= self.max_retries:
                    raise
                time.sleep(2 ** attempt)

    def health(self) -> Tuple[bool, Dict[str, Any]]:
        url = self._url("health")
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(url, headers=self.headers)
                if r.status_code >= 400:
                    return False, {"status_code": r.status_code, "text": r.text}
                try:
                    return True, r.json()
                except Exception:
                    return True, {"text": r.text}
        except Exception as e:
            logger.exception("GenericHTTPProvider.health error: %s", e)
            return False, {"error": str(e)}

    def list_models(self) -> List[Dict[str, Any]]:
        url = self._url("models")
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(url)
                r.raise_for_status()
                return r.json()
        except Exception as e:
            logger.exception("GenericHTTPProvider.list_models failed: %s", e)
            return []
