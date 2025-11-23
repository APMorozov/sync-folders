from FileHistory import FileHistory
from hash_compute import hash_file_sha1
from file_work import write_json, read_json


from pathlib import Path
from dataclasses import asdict
import json


class DirHistory:
    root: Path
    files: dict[str, FileHistory]

    def __init__(self, root: Path, setting_dir: Path):
        self.root = root
        self.files = {}
        settings_dir_path = root / setting_dir / Path("history.json")
        settings_dir_path.parent.mkdir(parents=True, exist_ok=True)
        if not settings_dir_path.exists():
            settings_dir_path.touch()
            write_json(settings_dir_path.__str__(), {})
        files = read_json(settings_dir_path.__str__())
        keys = list(files.keys())
        for key in keys:
            self.files[key] = FileHistory(**files[key])

    def update_DirHistory_field(self, files: set):
        file_states = dict()
        for file in files:
            absolute_path = self.root / file
            mtime = absolute_path.stat().st_mtime
            hash = hash_file_sha1(absolute_path)
            deleted = False
            self.files[file] = FileHistory(mtime, hash, deleted)

    def update_history_file(self):
        dict_object = {}
        path_to_file = self.root / Path(".sync\\history.json")
        for key in self.files.keys():
            dict_object[key.__str__()] = asdict(self.files[key])
            write_json(path_to_file, dict_object)

    def is_deleted(self, current_path: Path):
        file_history = self.files[current_path.__str__()]
        return file_history.deleted

    def determine_files_to_delete(self, set_of_files: set):
        old_files = set(self.files.keys())
        set_with_files = set(file.__str__() for file in set_of_files)
        files_to_delete = []
        print("Set: ", set_with_files)
        print("OLD: ", old_files)
        for difference in (old_files - set_with_files):
            if self.files[difference].deleted:
                continue
            else:
                self.files[difference].deleted = True
                files_to_delete.append(difference)
        return files_to_delete




