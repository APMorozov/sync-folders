from FileHistory import FileHistory
from file_work import write_json, read_json
from hash_compute import hash_file_sha1


from dataclasses import asdict
from pathlib import Path


class DirHistory:
    """Класс реализующий логику ведения файловой истории"""
    root: Path
    files: dict[str, FileHistory]

    def __init__(self, root: Path, setting_dir: Path):
        """

        :param root: Путь до директории которую нужно синхронизировать
        :param setting_dir: директория с настройками
        """
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

    def update_DirHistory_field(self, files: set[Path]) -> None:
        """
        Добавляет новые файлы за которыми будет писаться история , либо обновляет значения файлов
        :param files: пути к файлам
        :return:
        """
        for file in files:
            absolute_path = self.root / file
            mtime = absolute_path.stat().st_mtime
            file_hash = hash_file_sha1(absolute_path)
            deleted = False
            self.files[file.__str__()] = FileHistory(mtime, file_hash, deleted)

    def update_history_file(self) -> None:
        """
        Записывает историю файлов в .sync\\history.json
        :return:
        """
        dict_object = {}
        path_to_file = self.root / Path(".sync\\history.json")
        for key in self.files.keys():
            dict_object[key.__str__()] = asdict(self.files[key])
            write_json(path_to_file, dict_object)

    def is_deleted(self, current_path: Path):
        """
        Проверяет не удален ли файл на носителе
        :param current_path: путь к файлу
        :return:
        """
        keys = self.files.keys()
        if current_path.__str__() not in keys:
            return False
        file_history = self.files[current_path.__str__()]
        return file_history.deleted

    def set_flag_deleted_at(self, current_path: Path):
        keys = self.files.keys()
        if current_path.__str__() not in keys:
            raise Exception
        file_history = self.files[current_path.__str__()]
        file_history.deleted_at = True

    def delete_files_from_history(self, files: set[Path]):
        for file in files:
            if self.files[file.__str__()].deleted and self.files[file.__str__()].deleted_at:
                self.files.pop(file.__str__())

    def determine_files_to_delete(self, set_of_files: set[Path]) -> set[Path]:
        """
        Находит файлы которые были удалены пользователем(на основе различий между сканированиями)
        :param set_of_files: пути к файлам
        :return: пути к файлам обязательным к удалению
        """
        old_files = set(self.files.keys())
        set_with_files = set(file.__str__() for file in set_of_files)
        files_to_delete = set()
        for difference in (old_files - set_with_files):
            if self.files[difference].deleted:
                continue
            else:
                self.files[difference].deleted = True
                files_to_delete.add(Path(difference))
        return files_to_delete
