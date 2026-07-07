from typing import Any, Dict, Iterable, Tuple, List
import httpx
import logging
from backend.app.services.providers.base import ProviderAdapter

logger = logging.getLogger("model.providers.openai")

class OpenAIAdapter(ProviderAdapter):
    """Adapter for OpenAI-compatible APIs (chat/completions and streaming delta).

    Configuration (via config dict):
    - api_url: base URL (e.g., https://api.openai.com)
    - api_key: optional API key to forward as Authorization header
    - model: model name
    - timeout, max_retries
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        self.timeout = config.get("timeout", 60)
        self.max_retries = int(config.get("max_retries", 3))

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.api_url.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **(kwargs.get("params") or {})
        }
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(url, json=payload, headers=self._headers())
            r.raise_for_status()
            return r.json()

    def stream(self, prompt: str, **kwargs) -> Iterable[str]:
        url = f"{self.api_url.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            **(kwargs.get("params") or {})
        }
        with httpx.stream("POST", url, json=payload, headers=self._headers(), timeout=self.timeout) as resp:
            resp.raise_for_status()
            for raw in resp.iter_bytes(chunk_size=1024):
                if not raw:
                    continue
                text = raw.decode(errors="ignore")
                # OpenAI streaming emits data: <json>\n\n
                parts = text.splitlines()
                for p in parts:
                    p = p.strip()
                    if not p or p == "data: [DONE]":
                        continue
                    if p.startswith("data:"):
                        p = p[len("data:"):].strip()
                    try:
                        import json
                        j = json.loads(p)
                        # navigate to delta content
                        choices = j.get("choices")
                        if choices and isinstance(choices, list):
                            delta = choices[0].get("delta", {})
                            text_piece = delta.get("content") or delta.get("token")
                            if text_piece:
                                yield text_piece
                            else:
                                # non-text delta
                                continue
                        else:
                            # fallback
                            yield p
                    except Exception:
                        yield p

    def health(self) -> Tuple[bool, Dict[str, Any]]:
        url = f"{self.api_url.rstrip('/')}/v1/models"
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(url, headers=self._headers())
                if r.status_code >= 400:
                    return False, {"status_code": r.status_code, "text": r.text}
                try:
                    return True, r.json()
                except Exception:
                    return True, {"text": r.text}
        except Exception as e:
            logger.exception("OpenAIAdapter.health error: %s", e)
            return False, {"error": str(e)}

    def list_models(self) -> List[Dict[str, Any]]:
        ok, info = self.health()
        if ok:
            try:
                return info.get("data") if isinstance(info, dict) else []
            except Exception:
                return []
        return []
