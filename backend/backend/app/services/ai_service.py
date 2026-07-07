import httpx
import time
from backend.app.core.config import settings
from typing import Generator, Tuple

class AIService:
    def __init__(self):
        self.base_url = settings.MODEL_API_URL.rstrip("/")
        self.timeout = settings.MODEL_REQUEST_TIMEOUT
        self.max_retries = settings.MODEL_MAX_RETRIES

    def generate_response(self, prompt: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}/generate"
        payload = {"prompt": prompt}
        if params:
            payload.update(params)
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    r = client.post(url, json=payload)
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                if attempt + 1 >= self.max_retries:
                    raise
                time.sleep(2 ** attempt)

    def stream_response(self, prompt: str, params: dict | None = None) -> Generator[str, None, None]:
        """Streams tokens from the model server. Assumes the model supports a /stream endpoint that yields newline-delimited JSON with {token: "..."} or plain text chunks."""
        url = f"{self.base_url}/stream"
        payload = {"prompt": prompt}
        if params:
            payload.update(params)
        for attempt in range(self.max_retries):
            try:
                with httpx.stream("POST", url, json=payload, timeout=self.timeout) as resp:
                    resp.raise_for_status()
                    for raw in resp.iter_bytes(chunk_size=1024):
                        if not raw:
                            continue
                        text = raw.decode(errors="ignore")
                        # split by newlines and yield non-empty
                        parts = text.splitlines()
                        for p in parts:
                            token = p.strip()
                            if not token:
                                continue
                            # try to parse as json {"token": "..."}
                            try:
                                import json
                                j = json.loads(token)
                                if isinstance(j, dict) and j.get("token"):
                                    yield j.get("token")
                                    continue
                            except Exception:
                                pass
                            yield token
                    return
            except Exception as e:
                if attempt + 1 >= self.max_retries:
                    raise
                time.sleep(2 ** attempt)

    def health_check(self) -> Tuple[bool, dict]:
        url = f"{self.base_url}/health"
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(url)
                r.raise_for_status()
                return True, r.json()
        except Exception as e:
            return False, {"error": str(e)}
