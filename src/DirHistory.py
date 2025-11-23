from FileHistory import FileHistory
from hash_compute import hash_file_sha1
from file_work import write_json, read_json, write_empty_json


from pathlib import Path
from dataclasses import asdict
import json


class DirHistory:
    root: Path
    files: dict[str, FileHistory] = {}

    def __init__(self, root: Path, setting_dir: Path):
        self.root = root
        settings_dir_path = root / setting_dir / Path("history.json")
        settings_dir_path.parent.mkdir(parents=True, exist_ok=True)
        if not settings_dir_path.exists():
            settings_dir_path.touch()
            write_json(settings_dir_path, {})
        files = read_json(settings_dir_path)
        try:
            keys = list(files.keys())
            for key in keys:
                self.files[key] = FileHistory(json.loads(files[key]))
        except Exception:
            self.files = {}

    def update_DirHistory_field(self, files: set):
        file_states = dict()
        for file in files:
            absolute_path = self.root / file
            mtime = absolute_path.stat().st_mtime
            hash = hash_file_sha1(absolute_path)
            deleted = False
            self.files[file] = FileHistory(mtime, hash, deleted)

    def update_history_file(self, ):
        dict_object = {}
        path_to_file = self.root / Path(".sync\\history.json")
        for key in self.files.keys():
            print("Key: ", type(key))
            dict_object[key.__str__()] = asdict(self.files[key])
            write_json(path_to_file, dict_object)
