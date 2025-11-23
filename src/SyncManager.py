from Scanner import Scanner
from Comparer import Comparer
from Synchronizer import Synchronizer
from DirHistory import DirHistory
from file_work import read_json
import json

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

    def check_sync(self):
        pc_set_of_files = Scanner.scan_folder(self.pc_folder, self.ignore_files)
        flash_set_of_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        print(pc_set_of_files)
        print(flash_set_of_files)
        #self.pc_DirHistory.update_DirHistory_field(pc_set_of_files)
        #self.pc_DirHistory.update_history_file()

        #self.flash_DirHistory.update_DirHistory_field(flash_set_of_files)
        #self.flash_DirHistory.update_history_file()

        no_on_pc, no_on_flash = Comparer.take_differences(pc_set_of_files, flash_set_of_files)

        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)

        print("DELETED1: ", self.pc_DirHistory.is_deleted(Path("super_secret.txt")))
        print("DELETED2: ", self.pc_DirHistory.is_deleted(Path("flash.txt")))

        must_be_sync = Comparer.resolve_sync_actions(no_on_pc, self.pc_DirHistory)
        print("Must sync: ", must_be_sync)

        self.Synchronizer.synchronize(must_be_sync, no_on_flash)

        files_to_delete = self.pc_DirHistory.determine_files_to_delete(pc_set_of_files)
        print("Files to delete: ", files_to_delete)

