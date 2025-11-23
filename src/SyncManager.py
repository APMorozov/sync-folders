from Scanner import Scanner
from Comparer import Comparer
from Synchronizer import Synchronizer
from DirHistory import DirHistory
from file_work import read_json
import json



"""Модуль реализующий логику всего ПО"""


class SyncManager:
    def __init__(self, config: json):
        """
        Создание класса
        :param config: JSON конфиг
        """
        self.pc_folder = config["pc_folder"]
        self.flash_folder = config["flash_folder"]
        self.history = config["history"]
        self.sync_interval_sec = config["sync_interval_sec"]
        self.Synchronizer = Synchronizer(self.pc_folder, self.flash_folder)
        self.DirHistory = DirHistory(self.pc_folder, read_json(self.history))

    def check_sync(self):
        pc_set_of_files = Scanner.scan_folder(self.pc_folder, len(self.pc_folder))
        flash_set_of_files = Scanner.scan_folder(self.flash_folder, len(self.flash_folder))
        print(pc_set_of_files)
        print(flash_set_of_files)
        self.DirHistory.update_DirHistory_field(pc_set_of_files)
        self.DirHistory.update_history_file(self.history)
        no_on_pc, no_on_flash = Comparer.compare_dirs(pc_set_of_files, flash_set_of_files)

        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)

        self.Synchronizer.synchronize(no_on_pc, no_on_flash)

