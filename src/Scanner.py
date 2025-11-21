from pathlib import Path


class Scanner:
    @staticmethod
    def scan_folder(path_to_folder, len_root_dir):
        list_of_files = []
        path_folder = Path(path_to_folder)
        parts = path_folder.parts
        print("Parts: ", parts)
        for dir in path_folder.walk():
            for files in dir[2]:
                absolute_path = dir[0] / files
                parts_current_path_by_root = absolute_path.parts[len(parts):]
                list_of_files.append(Path(*parts_current_path_by_root))
        return set(list_of_files)
