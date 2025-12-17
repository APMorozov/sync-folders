from src.core.Scanner import Scanner
from src.core.Synchronizer import Synchronizer

import json
from pathlib import Path
import string
import random



"""Модуль реализующий логику всего ПО"""


class SyncManager:
    def __init__(self, config: json):
        """
        Создание класса
        :param config: JSON конфиг
        """
        self.pc_folder = config["pc_folder"]
        self.flash_folder = config["flash_folder"]
        self.ignore_files = config["ignore_files"]
        self.settings_dir = Path(".sync")
        self.Synchronizer = Synchronizer(self.pc_folder, self.flash_folder)

    def _generate_code(self, length: int = 10) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    def initialize_flash(self) -> bool:
        """
        Создаёт структуру на флешке для валидации:
        <flash_root>/<pc_folder_name>/.sync/code

        :return: True если создано / уже существует
        """
        try:

            flash_root = Path(self.flash_folder)


            target_dir = flash_root / Path(self.pc_folder).name


            sync_dir = target_dir / Path(self.settings_dir)


            code_file = sync_dir / Path("code")

            target_dir.mkdir(parents=True, exist_ok=True)
            sync_dir.mkdir(parents=True, exist_ok=True)

            if not code_file.exists():
                code = self._generate_code()
                code_file.parent.mkdir(parents=True, exist_ok=True)
                code_file.write_text(code, encoding="utf-8")

                print("Flash initialized with code:", code)
            else:
                print("Flash already initialized")

            return True

        except Exception as e:
            print("ERRRRRROR; ", e)
            return False
        
    def sync(self):
        pc_set_of_files = Scanner.scan_folder(self.pc_folder, self.ignore_files)
        flash_set_of_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        print("Files on pc: ", pc_set_of_files)
        print("Files on flash", flash_set_of_files)
        print("\n\n\n")
        no_on_pc, no_on_flash = Scanner.take_differences(pc_set_of_files, flash_set_of_files)
        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)
        print("\n\n\n")

        self.Synchronizer.copy_files(no_on_flash)
        self.Synchronizer.delete_files(no_on_pc)
        pc_empty_dir = Scanner.take_empty_dir(self.pc_folder)
        flash_empty_dir = Scanner.take_empty_dir(self.flash_folder)
        print("Empty pc: ", pc_empty_dir)
        print("Empty flash: ", flash_empty_dir)
        self.Synchronizer.delete_empty_dir(pc_empty_dir)
        self.Synchronizer.delete_empty_dir(flash_empty_dir)
        self.Synchronizer.update_files(pc_set_of_files)





