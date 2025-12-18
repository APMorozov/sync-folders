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

    def update_config(self, config: json):
        self.pc_folder = config["pc_folder"]
        self.flash_folder = config["flash_folder"]
        self.ignore_files = config["ignore_files"]
        self.Synchronizer.update_config(Path(self.pc_folder), Path(self.flash_folder))

    def _generate_code(self, length: int = 10) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    def write_code_to_pc(self, code):
        sync_dir = Path(self.pc_folder) / Path(self.settings_dir)
        code_file = sync_dir / Path("code")
        code_file.parent.mkdir(parents=True, exist_ok=True)
        code_file.write_text(code, encoding="utf-8")

    def initialize_flash(self) -> bool:
        """
        Создаёт структуру на флешке для валидации:
        <flash_root>/<pc_folder_name>/.sync/code

        :return: True если создано / уже существует
        """
        try:
            sync_dir = Path(self.flash_folder) / Path(self.settings_dir)

            code_file = sync_dir / Path("code")

            sync_dir.mkdir(parents=True, exist_ok=True)
            print("code_file: ", code_file)

            code = self._generate_code()
            code_file.parent.mkdir(parents=True, exist_ok=True)
            code_file.write_text(code, encoding="utf-8")
            self.write_code_to_pc(code)

            print("Flash initialized with code:", code)
            return True

        except Exception as e:
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

        errors_copy, copied_files = self.Synchronizer.copy_files(no_on_flash)
        self.Synchronizer.delete_files(no_on_pc)
        pc_empty_dir = Scanner.take_empty_dir(self.pc_folder)
        flash_empty_dir = Scanner.take_empty_dir(self.flash_folder)
        print("Empty pc: ", pc_empty_dir)
        print("Empty flash: ", flash_empty_dir)
        self.Synchronizer.delete_empty_dir(pc_empty_dir)
        self.Synchronizer.delete_empty_dir(flash_empty_dir)
        errors_update, updated_files = self.Synchronizer.update_files(pc_set_of_files)
        return errors_copy | errors_update, copied_files, updated_files





