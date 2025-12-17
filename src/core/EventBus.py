from pathlib import Path
import psutil
from PySide6.QtCore import Signal, QObject
import time

"""Класс реализующий логику мониторинга подключенных устройств и сигнализацию о новых подключениях"""

class EventBus(QObject):
    usb_detected = Signal(Path)

    def __init__(self, pc_folder: str):
        super().__init__()
        self.pc_folder_name = Path(pc_folder).name

    def usb_monitor(self):
        known = set()

        while True:
            drives = {
                d.device for d in psutil.disk_partitions()
                if "removable" in d.opts
            }

            new_drives = drives - known

            for drive in new_drives:
                if self._is_valid_flash(drive):
                    # ⬅️ ВАЖНО: передаём КОРЕНЬ ФЛЕШКИ
                    self.usb_detected.emit(Path(drive) / Path(self.pc_folder_name))

            known = drives
            time.sleep(1)

    def _is_valid_flash(self, drive: str) -> bool:
        drive = Path(drive)
        return (
            (drive / self.pc_folder_name).is_dir()
            and (drive / self.pc_folder_name / ".sync").is_dir()
            and (drive / self.pc_folder_name / ".sync" / "code").is_file()
        )
