from pathlib import Path
import psutil
from PySide6.QtCore import Signal, QObject
import time

"""Класс реализующий логику мониторинга подключенных устройств и сигнализацию о новых подключениях"""


class EventBus(QObject):
    usb_detected = Signal(Path)

    def __init__(self, pc_folder: str):
        super().__init__()
        self.pc_folder = Path(pc_folder)

    def update_pc_folder(self, pc_folder: str):
        self.pc_folder = Path(pc_folder)

    def usb_monitor(self):
        known = set()

        while True:
            drives = {
                d.device for d in psutil.disk_partitions()
                if "removable" in d.opts
            }

            new_drives = drives - known

            for drive in new_drives:
                if self.is_valid_flash(drive):
                    self.usb_detected.emit(Path(drive) / Path(self.pc_folder).name)

            known = drives
            time.sleep(1)

    def is_valid_flash(self, drive: str) -> bool:
        drive = Path(drive)
        pc_folder_name = self.pc_folder.name
        print("Drive: ", drive)
        valid = (((drive / pc_folder_name).is_dir()
                 and (drive / pc_folder_name / ".sync").is_dir())
                 and (drive / pc_folder_name / ".sync" / "code").is_file())
        if valid:
            flash_code = (drive / pc_folder_name / ".sync" / "code")
            pc_code = (self.pc_folder / ".sync" / "code")
            if flash_code.read_text("utf-8") == pc_code.read_text("utf-8"):
                return True
        return False
