from Scanner import Scanner
from Comparer import Comparer
from Synchronizer import Synchronizer
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
        self.sync_interval_sec = config["sync_interval_sec"]
        self.Synchronizer = Synchronizer(self.pc_folder, self.flash_folder)

    def check_sync(self):
        pc_set_of_files = Scanner.scan_folder(self.pc_folder, len(self.pc_folder))
        flash_set_of_files = Scanner.scan_folder(self.flash_folder, len(self.flash_folder))
        print(pc_set_of_files)
        print(flash_set_of_files)

        no_on_pc, no_on_flash = Comparer.compare_dirs(pc_set_of_files, flash_set_of_files)

        print("No on pc: ", no_on_pc)
        print("No on flash", no_on_flash)

        self.Synchronizer.synchronize(no_on_pc, no_on_flash)

