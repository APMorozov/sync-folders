import json
from pathlib import Path
from src.core.FileState import FileState


class StateManager:

    @staticmethod
    def load(path: Path) -> dict[Path, FileState]:
        if not path.exists():
            return {}

        data = json.loads(path.read_text(encoding="utf-8"))
        result = {}

        for k, v in data.get("files", {}).items():
            result[Path(k)] = FileState(v["hash"], v["mtime"])

        return result

    @staticmethod
    def save(path: Path, snapshot: dict[Path, FileState]):
        data = {
            "files": {
                str(k): {"hash": v.hash, "mtime": v.mtime}
                for k, v in snapshot.items()
            }
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=4), encoding="utf-8")
