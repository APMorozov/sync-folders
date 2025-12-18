from src.utils.hash_compute import hash_file_sha1

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

    def update_config(self, pc_folder: Path, flash_folder: Path):
        self.pc_folder = pc_folder
        self.flash_folder = flash_folder

    def copy_files(self, files):
        """
        Копирует файлы на флэшку
        :param files: файлы для копирования
        :return:
        """
        for file in files:
            path = self.flash_folder / file
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.pc_folder / file, path,)

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
        files_to_update = set()
        for file in files:
            path_to_pc_file = self.pc_folder / file
            path_to_flash_file = self.flash_folder / file
            if hash_file_sha1(path_to_pc_file.__str__()) != hash_file_sha1(path_to_flash_file.__str__()):
                files_to_update.add(file)
        self.copy_files(files_to_update)


