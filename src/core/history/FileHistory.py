from dataclasses import dataclass


@dataclass
class FileHistory:
    """
    класс реализующий хранение данных касающихся истории файла
    """
    mtime: int | None = None
    hash: str | None = None
    deleted: bool = False
    deleted_at: bool | None = None
