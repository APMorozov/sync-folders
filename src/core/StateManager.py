from src.utils.hash_compute import hash_file_sha1

import json
from pathlib import Path
import time


class StateManager:
    """
    Класс реализующий управления файлом состояний
    """
    def __init__(self, flash_folder: Path):
        self.flash_folder = Path(flash_folder)
        self.state_file = self.flash_folder / ".sync" / "state.json"
        self.state = {"files": {}}
        self.load_state()

    def add_one_file_to_state(self, file: str) -> None:
        """
        Добавляе одни файл в state
        :param file: путь к файлу
        :return:
        """
        info = self.state["files"].get(file, {})
        info["hash"] = hash_file_sha1((self.flash_folder / file).as_posix())
        info["deleted"] = False
        info["deleted_at"] = None
        self.state["files"][file] = info

    def make_new_state(self, flash_files: set[Path]) -> None:
        """
        Создает новый state
        :param flash_files: файлы для записи в state
        :return:
        """
        for file in flash_files:
            self.add_one_file_to_state(file.as_posix())

    def supplement_files_to_state(self, flash_files: set[Path]) -> None:
        """
        добавить файлы в уже существующий state
        :param flash_files: файлы
        :return:
        """
        for file in flash_files:
            files_in_sates = self.state["files"].keys()
            str_file = file.as_posix()
            if str_file not in files_in_sates:
                self.add_one_file_to_state(str_file)

    def load_state(self) -> None:
        """
        Загрузить state в переменные класса
        :return:
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                self.state = {"files": {}}

    def save_state(self) -> None:
        """
        Сохранить state из поля класса в Файл state
        :return:
        """
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def update_file(self, rel_path: str, abs_path: Path, deleted=False) -> None:
        """
        Добавляет или обновляет запись файла в state.json
        """
        info = self.state["files"].get(rel_path, {})
        info["hash"] = hash_file_sha1(abs_path.as_posix()) if not deleted else info.get("hash")
        info["deleted"] = deleted
        info["deleted_at"] = time.time() if deleted else None
        self.state["files"][rel_path] = info

    def mark_deleted(self, rel_path: str) -> None:
        """
        Пометить файл удаланным
        :param rel_path: путь к файлу
        :return:
        """
        if rel_path in self.state["files"]:
            self.state["files"][rel_path]["deleted"] = True
            self.state["files"][rel_path]["deleted_at"] = time.time()

    def is_deleted(self, rel_path: str) -> tuple[bool, float | None]:
        """
        Удален ли файл
        :param rel_path:
        :return: Если удален (True, Время удаления) иначе (False, None)
        """
        info = self.state.get("files", {}).get(rel_path, {})
        deleted = info.get("deleted", False)
        deleted_at = info.get("deleted_at", None)
        return deleted, deleted_at

