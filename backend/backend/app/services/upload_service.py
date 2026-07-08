# Minimal upload processing service (synchronous)
import os
from backend.app.core.config import settings

class UploadService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, filename: str, contents: bytes) -> str:
        path = os.path.join(self.upload_dir, filename)
        with open(path, "wb") as f:
            f.write(contents)
        return path

