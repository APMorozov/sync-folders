from src.Scanner import Scanner
from src.Comparer import Comparer
from src.Synchronizer import Synchronizer
from src.DirHistory import DirHistory
from src.file_work import read_json

import json
import time
from pathlib import Path



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
        self.sync_interval_sec = config["sync_interval_sec"]
        self.Synchronizer = Synchronizer(self.pc_folder, self.flash_folder)
        self.pc_DirHistory = DirHistory(self.pc_folder, self.settings_dir)
        self.flash_DirHistory = DirHistory(self.flash_folder, self.settings_dir)

    def start_sync(self):
        pc_set_of_files = Scanner.scan_folder(self.pc_folder, self.ignore_files)
        flash_set_of_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        print(pc_set_of_files)
        print(flash_set_of_files)
        self.pc_DirHistory.update_DirHistory_field(pc_set_of_files)
        self.pc_DirHistory.update_history_file()

        self.flash_DirHistory.update_DirHistory_field(flash_set_of_files)
        self.flash_DirHistory.update_history_file()

        no_on_pc, no_on_flash = Comparer.take_differences(pc_set_of_files, flash_set_of_files)

        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)

        pc_must_be_sync = Comparer.resolve_sync_actions(no_on_pc, self.pc_DirHistory)
        print("Must sync: ", pc_must_be_sync)

        flash_must_be_sync = Comparer.resolve_sync_actions(no_on_flash, self.flash_DirHistory)
        print("Must sync: ", flash_must_be_sync)

        self.Synchronizer.synchronize(pc_must_be_sync, flash_must_be_sync)
        self.Synchronizer.synchronize(pc_must_be_sync, flash_must_be_sync)
        self.pc_DirHistory.update_DirHistory_field(pc_must_be_sync)
        self.flash_DirHistory.update_DirHistory_field(flash_must_be_sync)
        self.flash_DirHistory.update_history_file()
        self.pc_DirHistory.update_history_file()

    def find_and_sinc_deleted_files(self, pc_set_of_files: set[Path], flash_set_of_files: set[Path]):
        pc_files_to_delete = self.pc_DirHistory.determine_files_to_delete(pc_set_of_files)
        print("Delete on pc: ", pc_files_to_delete)
        self.Synchronizer.sinchronize_deleted_files(pc_files_to_delete, self.pc_DirHistory, self.flash_DirHistory)

        flash_files_to_delete = self.flash_DirHistory.determine_files_to_delete(flash_set_of_files)
        print("Delete on flash: ", flash_files_to_delete)
        self.Synchronizer.sinchronize_deleted_files(flash_files_to_delete, self.flash_DirHistory, self.pc_DirHistory)

        return pc_files_to_delete, flash_files_to_delete

    def go(self):
        pc_set_of_files = Scanner.scan_folder(self.pc_folder, self.ignore_files)
        flash_set_of_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        print("Files on pc: ", pc_set_of_files)
        print("Files on flash", flash_set_of_files)
        print("\n\n\n")

        pc_files_to_delete, flash_files_to_delete = self.find_and_sinc_deleted_files(pc_set_of_files,
                                                                                     flash_set_of_files)

        no_on_pc, no_on_flash = Comparer.take_differences(pc_set_of_files, flash_set_of_files)
        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)
        print("\n\n\n")

        pc_must_be_sync = Comparer.resolve_sync_actions(no_on_pc, self.pc_DirHistory)
        flash_must_be_sync = Comparer.resolve_sync_actions(no_on_flash, self.flash_DirHistory)
        print("Must be sync pc: ", pc_must_be_sync)
        print("Must be sync flash", flash_must_be_sync)
        print("\n\n\n")

        self.Synchronizer.synchronize(pc_must_be_sync, flash_must_be_sync)

        self.pc_DirHistory.delete_files_from_history(pc_files_to_delete)
        self.flash_DirHistory.delete_files_from_history(flash_files_to_delete)
        self.flash_DirHistory.delete_files_from_history(pc_files_to_delete)
        self.pc_DirHistory.delete_files_from_history(flash_files_to_delete)

        self.pc_DirHistory.update_DirHistory_field(pc_must_be_sync)
        self.flash_DirHistory.update_DirHistory_field(flash_must_be_sync)
        self.flash_DirHistory.update_history_file()
        self.pc_DirHistory.update_history_file()


