from src.utils.file_work import read_json, write_json

from pathlib import Path
import psutil
from PySide6.QtCore import Signal, QObject
import time

"""Класс реализующий логику мониторинга подключенных устройств и валидации"""


class Validator(QObject):
    usb_detected = Signal(Path)

    def __init__(self, pc_folder: str):
        super().__init__()
        self.pc_folder = Path(pc_folder)

    def update_pc_folder(self, pc_folder: str):
        """
        Обновление пути к папке на пк
        :param pc_folder: путь к папке на пк
        :return:
        """
        self.pc_folder = Path(pc_folder)

    def usb_monitor(self) -> None:
        """
        Мониторинг, новых подключений
        :return: Найдена ли иницциализированная флэшка
        """
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
        """
        Валидация флэшки
        :param drive: корень флэшки
        :return: Инициализированная ли флэшка
        """
        drive = Path(drive)
        pc_folder_name = self.pc_folder.name
        valid = (((drive / pc_folder_name).is_dir()
                 and (drive / pc_folder_name / ".sync").is_dir())
                 and (drive / pc_folder_name / ".sync" / "code").is_file())
        if valid:
            flash_code = (drive / pc_folder_name / ".sync" / "code")
            pc_code = (self.pc_folder / ".sync" / "code")
            if flash_code.read_text("utf-8") == pc_code.read_text("utf-8"):
                return True
        return False

    @staticmethod
    def load_or_create_config(path: str) -> None:
        """
        Валидация конфига настроек
        :param path: путь до конфига
        :return:
        """
        default_config = {
            "pc_folder": "",
            "flash_folder": "",
            "ignore_files": [".sync"]
        }
        config_path = Path(path)

        if not config_path.exists():
            write_json(path, default_config)
            return

        if config_path.stat().st_size == 0:
            write_json(path, default_config)
            return

        try:
            data = read_json(path)
        except Exception:
            write_json(path, default_config)
            return

        if not isinstance(data, dict):
            write_json(path, default_config)
            return

        fixed = default_config.copy()
        fixed.update(data)

        if ".sync" not in fixed["ignore_files"]:
            fixed["ignore_files"].insert(0, ".sync")

        write_json(path, fixed)
