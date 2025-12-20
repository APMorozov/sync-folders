from src.utils.hash_compute import hash_file_sha1
from src.core.SyncPlanner import Action
from src.core.StateManager import StateManager

from dataclasses import dataclass
from pathlib import Path
import shutil
import os


@dataclass
class SyncInfo:
    file: Path
    reason: str

    def __eq__(self, other):
        return isinstance(other, SyncInfo) and self.file == other.file and self.reason == other.reason

    def __hash__(self):
        return hash((self.file, self.reason))


class Synchronizer:
    """
    класс реализующий логику синхронизации директорий
    """
    def __init__(self, pc_folder: Path, flash_folder: Path):
        self.pc_folder = pc_folder
        self.flash_folder = flash_folder

    def update_config(self, pc_folder: Path, flash_folder: Path):
        self.pc_folder = pc_folder
        self.flash_folder = flash_folder

    def copy_files(self, files):
        """
        Копирует файлы на флэшку
        :param files: файлы для копирования
        :return:
        """

        errors = set()
        copied_files = []

        for file in files:
            src = self.pc_folder / file
            dst = self.flash_folder / file

            dst.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(src, dst)
                copied_files.append(SyncInfo(src, "Файл успешно скопирован"))
            except PermissionError:
                errors.add(SyncInfo(src, "Файл занят другим процессом(попробуйте закрыть и повторить синхронизацию)"))
            except Exception as e:

                errors.add(SyncInfo(src, str(e)))

        return errors, copied_files

    def copy_one_file(self, src: Path, dst: Path):
        """
        Копирует один файл безопасно:
        - создаёт папки
        - использует tmp + replace
        """
        dst.parent.mkdir(parents=True, exist_ok=True)

        tmp = dst.with_suffix(dst.suffix + ".tmp")

        try:
            shutil.copy2(src, tmp)
            tmp.replace(dst)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except Exception:
                    pass

    def apply_plan(self, plan: dict[Path, Action], state: StateManager):
        errors = []
        copied = []
        deleted = []

        for file, action in plan.items():
            pc = self.pc_folder / file
            fl = self.flash_folder / file

            try:
                if action == Action.COPY_TO_FLASH:
                    fl.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(pc, fl)
                    state.update_file(file.as_posix(), fl)
                    copied.append(SyncInfo(file, "Файл успешно скопирован"))

                elif action == Action.COPY_TO_PC:
                    pc.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(fl, pc)
                    state.update_file(file.as_posix(), pc)
                    copied.append(SyncInfo(file, "Файл успешно скопирован"))

                elif action == Action.DELETE_PC and pc.exists():
                    pc.unlink()
                    state.mark_deleted(file.as_posix())
                    deleted.append(SyncInfo(file, "Файл успешно удален"))

                elif action == Action.DELETE_FLASH and fl.exists():
                    fl.unlink()
                    state.mark_deleted(file.as_posix())
                    deleted.append(SyncInfo(file, "Файл успешно удален"))

                elif action == Action.CONFLICT:
                    errors.append(SyncInfo(file, "Конфликтный файл"))

            except Exception as e:
                errors.append(SyncInfo(file, f"Ошибка: {str(e)}"))

        return errors, copied, deleted

    def delete_files(self, files):
        """
        Удаляет файлы на флэшке
        :param files: файлы для удаления
        :return:
        """
        for file in files:
            os.remove(self.flash_folder / file)

    @staticmethod
    def delete_empty_dir(empty_dir: set[Path]):
        """
        Удаляет пустые директории поданные как параметр метода
        :param empty_dir: директории для удаления
        :return:
        """
        for dir in empty_dir:
            os.rmdir(dir)

    def update_files(self, files: set[Path]):
        """
        Обновляет файлы на основе разностей в хэше
        :param files: файлы в директории  (файлы должны быть и на флэшке и на пк)
        :return:
        """
        errors_hash = set()
        files_to_update = set()
        for file in files:
            path_to_pc_file = self.pc_folder / file
            path_to_flash_file = self.flash_folder / file
            try:
                if hash_file_sha1(path_to_pc_file.__str__()) != hash_file_sha1(path_to_flash_file.__str__()):
                    files_to_update.add(file)
            except PermissionError:
                errors_hash.add(
                    SyncInfo(path_to_pc_file, "Файл занят другим процессом(попробуйте закрыть и повторить синхронизацию)"))
            except Exception as e:

                errors_hash.add(SyncInfo(path_to_pc_file, str(e)))

        errors_copy, updated_files = self.copy_files(files_to_update)
        return errors_copy | errors_hash, updated_files

