from pathlib import Path


class Scanner:
    """
    Класс реализующий логику сканирования директорий
    """

    @staticmethod
    def scan_folder(path_to_folder: Path, ignore_folders: list) -> set[Path]:
        """
        Рекурсивное сканирование с учетом игнорируемых файлов
        :param path_to_folder: путь к папке для сканирования
        :param ignore_folders: игнорируемые файлы\папки
        :return: все файлы на папке
        """
        result = set()
        root = Path(path_to_folder)
        root_parts = root.parts

        for directory, _, files in root.walk():
            for file in files:
                abs_path = Path(directory) / file
                rel_parts = abs_path.parts[len(root_parts):]

                if any(p in ignore_folders for p in rel_parts):
                    continue

                rel_path = Path(*rel_parts)
                result.add(rel_path)

        return result

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
