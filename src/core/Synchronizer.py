from src.core.history.DirHistory import DirHistory

from pathlib import Path
import shutil
import os


class Synchronizer:
    """
    класс реализующий логику синхронизации директорий
    """
    def __init__(self, pc_folder: Path, flash_folder: Path):
        self.pc_folder = pc_folder
        self.flash_folder = flash_folder

    def synchronize(self, no_on_pc: set[Path], no_on_flash: set[Path]):
        """
        Копирование файлов между директориями
        :param no_on_pc: пути к файлам которых нет на пк(нужно удалить)
        :param no_on_flash: пути к файлам которых нет на флэшке
        :return:
        """
        for file in no_on_pc:
            os.remove(self.flash_folder / file)

        for file in no_on_flash:
            path = self.flash_folder / file
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.pc_folder / file, path,)

    def delete_empty_dir(self, empty_dir: set[Path]):
        for dir in empty_dir:
            os.rmdir(dir)

    def sinchronize_deleted_files(self, files: set[Path], deleted_file_history: DirHistory, delete_file_history: DirHistory) -> None:
        for file in files:
            try:
                os.remove(delete_file_history.root / file)
                deleted_file_history.set_flag_deleted_at(file)
                delete_file_history.set_flag_deleted_at(file)
                delete_file_history.set_flag_deleted(file)
            except FileNotFoundError:
                continue
            except Exception as exc:
                print("ERROR:", exc)


