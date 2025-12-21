from pathlib import Path
import hashlib


class Scanner:
    """
    Класс реализующий логику сканирования директорий
    """

    @staticmethod
    def hash_file(path: Path) -> str:
        h = hashlib.sha1()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def scan_folder(path_to_folder: Path, ignore_files: list) -> set[Path]:
        result = set()
        root = Path(path_to_folder)
        root_parts = root.parts

        for directory, _, files in root.walk():
            for file in files:
                abs_path = Path(directory) / file
                rel_parts = abs_path.parts[len(root_parts):]

                if any(p in ignore_files for p in rel_parts):
                    continue

                rel_path = Path(*rel_parts)
                result.add(rel_path)

        return result

    @staticmethod
    def take_differences(pc_set_of_files: set, flash_set_of_files: set) -> tuple[set[Path], set[Path]]:
        """
        Находит различия между директориями
        :param pc_set_of_files: файлы в директори на пк
        :param flash_set_of_files: файлы в директори на флэшке
        :return: файлы которых нет на пк, файлы которых нет на флэшке
        """
        no_on_pc = flash_set_of_files - pc_set_of_files
        no_on_flash = pc_set_of_files - flash_set_of_files
        return no_on_pc, no_on_flash

    @staticmethod
    def take_empty_dir(path_to_folder: Path) -> set[Path]:
        """
        Поиск всех пустых папок и подпапок в указанной директории
        :param path_to_folder: директория для поиска
        :return: сэт пустых папок
        """
        empty_dir = []
        path_folder = Path(path_to_folder)
        for directory in path_folder.walk():
            if not (directory[2] or directory[1]):
                empty_dir.append(directory[0])
        return set(empty_dir)
