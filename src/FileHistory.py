import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FileHistory:
    mtime: int | None = None
    hash: str | None = None
    deleted: bool = False
    deleted_at: bool | None = None



