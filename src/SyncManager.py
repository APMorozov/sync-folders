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
        self.pc_DirHistory.update_DirHistory_field(pc_set_of_files)
        self.pc_DirHistory.update_history_file()

        self.flash_DirHistory.update_DirHistory_field(flash_set_of_files)
        self.flash_DirHistory.update_history_file()

        no_on_pc, no_on_flash = Comparer.take_differences(pc_set_of_files, flash_set_of_files)

        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)

        print("DELETED: ", self.flash_DirHistory.is_deleted(Path("diir\subdir\secter_text.txt")))

        #self.Synchronizer.synchronize(no_on_pc, no_on_flash)

