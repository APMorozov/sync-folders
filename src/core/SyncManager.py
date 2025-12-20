from src.core.Scanner import Scanner
from src.core.Synchronizer import Synchronizer
from src.core.StateManager import StateManager
from src.core.SyncPlanner import SyncPlanner

import json
from pathlib import Path
import string
import random
import shutil




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

        :return: True если создано
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

    def copy_code_from_flash(self):
        """
        Копирует файл .sync/code с флэшки в .sync/code на ПК
        """

        flash_root = Path(self.flash_folder)
        pc_root = Path(self.pc_folder)

        src = flash_root / ".sync" / "code"
        dst = pc_root / ".sync" / "code"

        if not src.exists() or not src.is_file():
            raise FileNotFoundError(
                f"Файл {src} не найден на флэшке"
            )

        dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(src, dst)
        except PermissionError:
            raise PermissionError(
                f"Файл {dst} занят другим процессом"
            )

    def sync(self):
        pc_root = Path(self.pc_folder)
        flash_root = Path(self.flash_folder)
        ignore = self.ignore_files

        state_pc = pc_root / ".sync/state.json"
        state_flash = flash_root / ".sync/state.json"

        last = StateManager.load(state_pc)

        pc_now = Scanner.scan_folder(pc_root, ignore)
        flash_now = Scanner.scan_folder(flash_root, ignore)

        plan = SyncPlanner.build(pc_now, flash_now, last)

        synchronizer = Synchronizer(pc_root, flash_root)
        errors, copied, updated = synchronizer.apply(plan)

        new_snapshot = Scanner.scan_folder(pc_root, ignore)

        StateManager.save(state_pc, new_snapshot)
        StateManager.save(state_flash, new_snapshot)

        return errors, copied, updated





