from pathlib import Path


class Scanner:
    """
    Класс реализующий логику сканирования директорий
    """
    @staticmethod
    def scan_folder(path_to_folder: Path, ignore_files: list) -> set[Path]:
        """
        Сканирует директорию в обход игнорируемых файлов
        :param path_to_folder: путь к директроии
        :param ignore_files: игнорируемые файлы
        :return: пути к файлам
        """
        list_of_files = []
        path_folder = Path(path_to_folder)
        parts = path_folder.parts
        for directory in path_folder.walk():
            for files in directory[2]:
                absolute_path = directory[0] / files
                parts_current_path_by_root = absolute_path.parts[len(parts):]
                if not any(item in ignore_files for item in parts_current_path_by_root):
                    list_of_files.append(Path(*parts_current_path_by_root))
        return set(list_of_files)

    @staticmethod
    def take_empty_dir(path_to_folder: Path) -> set[Path]:
        empty_dir = []
        path_folder = Path(path_to_folder)
        for directory in path_folder.walk():
            if not (directory[2] or directory[1]):
                print("Directory 1: ", directory[1])
                print("Directory 2: ", directory[2])
                empty_dir.append(directory[0])
        return set(empty_dir)
