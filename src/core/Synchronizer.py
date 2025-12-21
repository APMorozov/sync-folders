from src.core.SyncPlanner import Action
from src.core.StateManager import StateManager

from dataclasses import dataclass
from pathlib import Path
import os
import shutil


@dataclass
class SyncInfo:
    """Класс реализует передачу информации о файле после синхронизации"""
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

    def update_config(self, pc_folder: Path, flash_folder: Path) -> None:
        """
        Обновить данные
        :param pc_folder:
        :param flash_folder:
        :return:
        """
        self.pc_folder = pc_folder
        self.flash_folder = flash_folder

    @staticmethod
    def delete_empty_dir(empty_dir: set[Path]):
        """
        Удаляет пустые директории поданные как параметр метода
        :param empty_dir: директории для удаления
        :return:
        """
        for dir in empty_dir:
            os.rmdir(dir)

    @staticmethod
    def copy_one_file(src: Path, dst: Path):
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

    def apply_plan(self, plan: dict[Path, Action],
                   state: StateManager) -> tuple[list[SyncInfo], list[SyncInfo], list[SyncInfo]]:
        """
        Применяет план синхронизации
        :param plan: план синхронизации
        :param state: состояния файлов
        :return: Ошибки, Скопированны\Обновленные, Удаленные
        """
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

                elif action == Action.UNKNOWN_FILE:
                    errors.append(SyncInfo(file, "Не известный файл"))

            except PermissionError:
                message = "Ошибка файл занят другой программой попробуйте закрыть ее и перезапустить синхронизацию."
                errors.append(SyncInfo(file, message))
            except Exception as e:
                errors.append(SyncInfo(file, f"Ошибка: {str(e)}"))

        return errors, copied, deleted





