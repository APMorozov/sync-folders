from src.core.Scanner import Scanner
from src.core.Synchronizer import Synchronizer, SyncInfo
from src.core.StateManager import StateManager
from src.core.SyncPlanner import SyncPlanner


import json
from pathlib import Path
import string
import random
import shutil




"""Модуль реализующий логику синхронизации"""


class SyncManager:
    def __init__(self, config: json):
        """
        Создание класса
        :param config: JSON конфиг
        """
        self.pc_folder = Path(config["pc_folder"])
        self.flash_folder = Path(config["flash_folder"])
        self.ignore_files = config["ignore_files"]
        self.settings_dir = Path(".sync")
        self.Synchronizer = Synchronizer(self.pc_folder, self.flash_folder)
        self.StateManager = StateManager(self.flash_folder)

    def update_config(self, config: json) -> None:
        """
        Обновление данных
        :param config: новые данные
        :return:
        """
        self.pc_folder = Path(config["pc_folder"])
        self.flash_folder = Path(config["flash_folder"])
        self.ignore_files = config["ignore_files"]
        self.Synchronizer.update_config(Path(self.pc_folder), Path(self.flash_folder))
        self.StateManager = StateManager(self.flash_folder)

    @staticmethod
    def _generate_code(length: int = 10) -> str:
        """
        Генерация кода который используется для валидации
        :param length:
        :return:
        """

        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    def write_code_to_pc(self, code: str) -> None:
        """
        Запись кода валидации в .sync на ПК
        :param code: код
        :return:
        """
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

    def sync_by_attach(self) -> tuple[list[SyncInfo], list[SyncInfo], list[SyncInfo]]:
        """
        Синхронизация при подключении флэшки либо изменении настроек
        :return: Ошибки, Скопированны\Обновленные, Удаленные
        """


        # Сканируем папки
        pc_files = Scanner.scan_folder(self.pc_folder, self.ignore_files)
        flash_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        print("ON PC FILES: ", pc_files)
        print("ON FLASH FILES: ", flash_files)

        no_on_pc, no_on_flash = Scanner.take_differences(pc_files, flash_files)
        print("\n\nNO ON PC: ", no_on_pc)
        print("NO ON FLASH: ", no_on_flash)

        state_file = self.flash_folder / self.settings_dir / "state.json"
        print("PATH TO STATE FILE: ", state_file)
        if not state_file.exists():
            self.StateManager.make_new_state(flash_files)

        self.StateManager.supplement_files_to_state(flash_files)
        self.StateManager.save_state()

        plan = SyncPlanner.get_sync_plan_for_attach_action(pc_files, flash_files, self.StateManager, self.pc_folder)

        print("PLAN: ", plan)
        errors, copied_files, updated_files = self.Synchronizer.apply_plan(plan, self.StateManager)
        flash_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        self.StateManager.supplement_files_to_state(flash_files)
        self.StateManager.save_state()

        pc_empty_dirs = Scanner.take_empty_dir(self.pc_folder)
        flash_empty_dirs = Scanner.take_empty_dir(self.flash_folder)
        self.Synchronizer.delete_empty_dir(pc_empty_dirs)
        self.Synchronizer.delete_empty_dir(flash_empty_dirs)

        return errors, copied_files, updated_files

    def sync_by_btn(self) -> tuple[list[SyncInfo], list[SyncInfo], list[SyncInfo]]:
        """
        Синхронизация при нажатии кнопки
        :return: Ошибки, Скопированны\Обновленные, Удаленные
        """
        print("SYNC BY BUTTON")
        pc_files = Scanner.scan_folder(self.pc_folder, self.ignore_files)
        flash_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        print("ON PC FILES: ", pc_files)
        print("ON FLASH FILES: ", flash_files)

        no_on_pc, no_on_flash = Scanner.take_differences(pc_files, flash_files)
        print("\n\nNO ON PC: ", no_on_pc)
        print("NO ON FLASH: ", no_on_flash)

        state_file = self.flash_folder / self.settings_dir / "state.json"
        print("PATH TO STATE FILE: ", state_file)
        if not state_file.exists():
            self.StateManager.make_new_state(flash_files)

        self.StateManager.save_state()

        plan = SyncPlanner.get_sync_plan_for_btn_action(pc_files, flash_files, self.StateManager, self.pc_folder)

        print("PLAN: ", plan)
        errors, copied_files, updated_files = self.Synchronizer.apply_plan(plan, self.StateManager)
        flash_files = Scanner.scan_folder(self.flash_folder, self.ignore_files)
        self.StateManager.supplement_files_to_state(flash_files)
        self.StateManager.save_state()

        pc_empty_dirs = Scanner.take_empty_dir(self.pc_folder)
        flash_empty_dirs = Scanner.take_empty_dir(self.flash_folder)
        self.Synchronizer.delete_empty_dir(pc_empty_dirs)
        self.Synchronizer.delete_empty_dir(flash_empty_dirs)

        return errors, copied_files, updated_files

    def copy_one_file(self, from_copy: Path, to_copy: Path) -> None:
        """
        Копирование одного файла
        :param from_copy: путь откуда копировать
        :param to_copy: путь куда копировать
        :return:
        """
        self.Synchronizer.copy_one_file(from_copy, to_copy)
