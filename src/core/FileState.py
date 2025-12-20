from dataclasses import dataclass

@dataclass(frozen=True)
class FileState:
    hash: str
    mtime: float
