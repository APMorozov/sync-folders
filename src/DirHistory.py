from FileHistory import FileHistory
from hash_compute import hash_file_sha1
from file_work import write_json


from pathlib import Path
from dataclasses import asdict
import json


class DirHistory:
    root: Path
    files: dict[str, FileHistory] = {}

    def __init__(self, root: Path, files: dict):
        self.root = root
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

    def update_history_file(self, path_to_file: str):
        dict_object = {}
        for key in self.files.keys():
            print("Key: ", type(key))
            dict_object[key.__str__()] = asdict(self.files[key])
            write_json(path_to_file, dict_object)
