from src.GUI.AttachFlashDialog import AttachFlashDialog
from src.GUI.SettingsDialog import SettingsDialog
from src.core.SyncManager import SyncManager
from src.core.Synchronizer import SyncInfo
from src.GUI.SyncResultDialog import SyncResultDialog
from src.core.Validator import Validator
from src.utils.file_work import write_json, read_json


from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QSystemTrayIcon, QMenu,
    QMessageBox
)
from PySide6.QtGui import QIcon
from pathlib import Path


class SyncApp(QWidget):
    def __init__(self, path_to_config: str):
        super().__init__()
        self.path_to_config = path_to_config

        Validator.load_or_create_config(self.path_to_config)
        self.Validator = Validator(read_json(path_to_config)["pc_folder"])
        self.Validator.usb_detected.connect(self.flash_find)
        self.Manager = SyncManager(read_json(self.path_to_config))

        self.init_ui()
        self.set_data_from_config(read_json(self.path_to_config))
        self.tray = QSystemTrayIcon(QIcon("images.jpg"), self)
        tray_menu = QMenu()
        tray_menu.addAction("Открыть", self.show_window)
        tray_menu.addAction("Выход", self.exit_app)
        self.tray.setContextMenu(tray_menu)

    def init_ui(self):
        self.setWindowTitle("Cинхронизатор файлов")
        self.resize(520, 400)

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(QLabel("Путь до папки на компьютере"))
        self.pc_folder = QLineEdit()
        self.pc_folder.setReadOnly(True)
        main_layout.addWidget(self.pc_folder)

        main_layout.addWidget(QLabel("Путь до папки на флэшке"))
        self.flash_folder = QLineEdit()
        self.flash_folder.setReadOnly(True)
        main_layout.addWidget(self.flash_folder)

        main_layout.addWidget(QLabel("Игнорируемые папки"))
        self.ignore_list = QListWidget()
        self.ignore_list.setDisabled(True)
        main_layout.addWidget(self.ignore_list)

        btn_settings = QPushButton("Настройки")
        btn_settings.clicked.connect(self.open_settings)

        btn_sync = QPushButton("Синхронизировать")
        btn_sync.clicked.connect(self.sync_by_btn)

        btn_tray = QPushButton("Свернуть в трэй")
        btn_tray.clicked.connect(self.hide_to_tray)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addWidget(btn_tray)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(btn_settings)
        bottom_buttons.addWidget(btn_sync)

        btn_attach = QPushButton("Присоединить флэшку")
        btn_attach.clicked.connect(self.attach_flash)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addWidget(btn_tray)
        bottom_buttons.addWidget(btn_attach)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(btn_settings)
        bottom_buttons.addWidget(btn_sync)

        main_layout.addLayout(bottom_buttons)

    def set_data_from_config(self, data: dict) -> None:
        """
        Установка данных из конфига в GUI
        :param data: данные
        :return:
        """
        self.pc_folder.setText(data.get("pc_folder", ""))
        self.flash_folder.setText(data.get("flash_folder", ""))
        self.ignore_list.clear()
        for folder in data.get("ignore_files", []):
            self.ignore_list.addItem(folder)

    def open_settings(self) -> None:
        """
        Открытие настроек.После закрытия данные обновляются
        :return:
        """
        dialog = SettingsDialog(read_json(self.path_to_config), self)

        if dialog.exec():
            new_config = dialog.get_config()
            pc_sync_dir = Path(new_config["pc_folder"])
            new_config["flash_folder"] = (Path(new_config["flash_folder"]) / pc_sync_dir.parts[-1]).as_posix()
            write_json(self.path_to_config, new_config)
            self.set_data_from_config(new_config)
            self.Manager.update_config(read_json(self.path_to_config))
            self.Manager.initialize_flash()
            self.Validator.update_pc_folder(new_config["pc_folder"])
            self.sync_by_attach()

    def attach_flash(self) -> None:
        """
        Подключение уже инициализированной флэшки.Автоматически обновляются данные в конфиге и классах
        :return:
        """

        dialog = AttachFlashDialog(self)

        if not dialog.exec():
            return

        result = dialog.get_result()

        new_config = read_json(self.path_to_config)

        new_config["pc_folder"] = result["pc_folder"]
        new_config["flash_folder"] = result["flash_folder"]

        write_json(self.path_to_config, new_config)

        # обновляем всё
        self.set_data_from_config(new_config)
        self.Manager.update_config(new_config)
        self.Validator.update_pc_folder(new_config["pc_folder"])

        self.Manager.copy_code_from_flash()

        QMessageBox.information(
            self,
            "Устройство присоединено",
            "Флэшка успешно присоединена,ностели синхронизированы."
        )

        self.sync_by_attach()

    def flash_find(self, path_flash: Path) -> None:
        """
        Обновляет данные при обнаружении инициализированной флэшки
        :param path_flash: путь к флэшке
        :return:
        """
        QMessageBox.information(self, "USB", "Обнаружено инициализированное устройство.")
        self.update_flash_path(path_flash)
        config = read_json(self.path_to_config)
        self.set_data_from_config(config)
        self.Manager.update_config(config)
        self.sync_by_attach()

    def update_flash_path(self, path_flash: Path):
        """
        Обнапляет путь до флэшки в конфиге
        :param path_flash: путь до флэшки
        :return:
        """
        data = read_json(self.path_to_config)
        data["flash_folder"] = str(path_flash)
        write_json(self.path_to_config, data)

    def sync_by_attach(self) -> None:
        """
        Синхронизация при присоединении флэшки и обновлении данных настроек
        :return:
        """
        config = read_json(self.path_to_config)

        pc_folder = config.get("pc_folder", "")
        flash_folder = config.get("flash_folder", "")

        if not pc_folder:
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не выбран путь к папке на компьютере.\n\n"
                "Откройте «Настройки» и укажите папку для синхронизации."
            )
            return

        if not flash_folder:
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не выбран путь к флэшке.\n\n"
                "Подключите флэшку или укажите путь в настройках."
            )
            return

        flash_root = Path(flash_folder).parts[0]

        if not self.Validator.is_valid_flash(flash_root):
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не обнаружена флэшка которая является валидной.\n\n"
                "Убедитесь, что подключено ранее инициализированное устройство."
            )
            return

        errors, copied_files, updated_files = self.Manager.sync_by_attach()
        dialog = SyncResultDialog(errors, copied_files, updated_files, parent=self)
        dialog.resolveRequested.connect(
            self.resolve_sync_error
        )
        dialog.exec()

    def resolve_sync_error(self, sync_info: SyncInfo, action: str) -> None:
        """
        Разрешение ошибок возникающих при синхронизации
        :param sync_info:
        :param action:
        :return:
        """
        file = sync_info.file
        if action == "use_pc":
            self.Manager.copy_one_file(self.Manager.pc_folder / file, self.Manager.flash_folder / file)
        if action == "use_flash":
            self.Manager.copy_one_file(self.Manager.flash_folder / file, self.Manager.pc_folder / file)
        if action == "sync":
            self.Manager.copy_one_file(self.Manager.flash_folder / file, self.Manager.pc_folder / file)
        if action == "keep":
            pass

    def sync_by_btn(self):
        """
        Синхронизация при нажатии кнопки
        :return:
        """
        config = read_json(self.path_to_config)

        pc_folder = config.get("pc_folder", "")
        flash_folder = config.get("flash_folder", "")

        if not pc_folder:
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не выбран путь к папке на компьютере.\n\n"
                "Откройте «Настройки» и укажите папку для синхронизации."
            )
            return

        if not flash_folder:
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не выбран путь к флэшке.\n\n"
                "Подключите флэшку или укажите путь в настройках."
            )
            return

        flash_root = Path(flash_folder).parts[0]

        if not self.Validator.is_valid_flash(flash_root):
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не обнаружена флэшка которая является валидной.\n\n"
                "Убедитесь, что подключено ранее инициализированное устройство."
            )
            return

        errors, copied_files, updated_files = self.Manager.sync_by_btn()
        dialog = SyncResultDialog(errors, copied_files, updated_files, parent=self)
        dialog.resolveRequested.connect(
            self.resolve_sync_error
        )
        dialog.exec()

    def hide_to_tray(self):
        """
        Скрыть в Trey
        :return:
        """
        self.tray.show()
        self.hide()

    def show_window(self):
        """
        Показать из Trey
        :return:
        """
        self.show()
        self.raise_()

    def exit_app(self):
        """
        Закрытие ПО из Trey
        :return:
        """
        self.tray.hide()
        QApplication.quit()



