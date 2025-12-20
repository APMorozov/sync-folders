from src.core.FileState import FileState

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
    def scan_folder(root: Path, ignore: list[str]) -> dict[Path, FileState]:
        snapshot = {}
        root_parts = root.parts

        for base, dirs, files in root.walk():
            rel_dir = Path(*base.parts[len(root_parts):])

            if any(p in ignore for p in rel_dir.parts):
                continue

            for name in files:
                full = base / name
                rel = rel_dir / name

                if any(p in ignore for p in rel.parts):
                    continue

                try:
                    snapshot[rel] = FileState(
                        hash=Scanner.hash_file(full),
                        mtime=full.stat().st_mtime
                    )
                except PermissionError:
                    continue

        return snapshot

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
