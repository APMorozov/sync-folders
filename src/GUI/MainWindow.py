from src.GUI.SettingsDialog import SettingsDialog
from src.core.EventBus import EventBus


from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QLineEdit, QSystemTrayIcon, QMenu,
    QMessageBox
)
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtCore import Qt
from pathlib import Path
import time

from src.core.SyncManager import SyncManager
from src.utils.file_work import write_json, read_json


class SyncApp(QWidget):
    def __init__(self, path_to_config: str):
        super().__init__()
        self.path_to_config = path_to_config

        EventBus.load_or_create_config(self.path_to_config)
        self.Bus = EventBus(read_json(path_to_config)["pc_folder"])
        self.Bus.usb_detected.connect(self.ask_password)


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
        btn_sync.clicked.connect(self.sync_action)

        btn_tray = QPushButton("Свернуть в трэй")
        btn_tray.clicked.connect(self.hide_to_tray)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addWidget(btn_tray)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(btn_settings)
        bottom_buttons.addWidget(btn_sync)

        main_layout.addLayout(bottom_buttons)


    def set_data_from_config(self, data: dict):
        self.pc_folder.setText(data.get("pc_folder", ""))
        self.flash_folder.setText(data.get("flash_folder", ""))
        self.ignore_list.clear()
        for folder in data.get("ignore_files", []):
            self.ignore_list.addItem(folder)

    def open_settings(self):
        dialog = SettingsDialog(read_json(self.path_to_config), self)

        if dialog.exec():
            new_config = dialog.get_config()
            pc_sync_dir = Path(new_config["pc_folder"])
            new_config["flash_folder"] = (Path(new_config["flash_folder"]) / pc_sync_dir.parts[-1]).__str__()
            write_json(self.path_to_config, new_config)
            self.set_data_from_config(new_config)
            self.Manager.update_config(read_json(self.path_to_config))
            self.Manager.initialize_flash()
            self.Bus.update_pc_folder(new_config["pc_folder"])


    def ask_password(self, path_flash: Path):
        QMessageBox.information(self, "USB", "Обнаружено устройство. Введите пароль.")
        self.update_flash_path(path_flash)
        config = read_json(self.path_to_config)
        self.set_data_from_config(config)
        self.Manager.update_config(config)
        self.sync_action()

    def update_flash_path(self, path_flash: Path):
        data = read_json(self.path_to_config)
        data["flash_folder"] = str(path_flash)
        write_json(self.path_to_config, data)

    def sync_action(self):
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

        if not self.Bus.is_valid_flash(flash_root):
            QMessageBox.warning(
                self,
                "Ошибка синхронизации",
                "Не обнаружена флэшка которая является валидной.\n\n"
                "Убедитесь, что подключено ранее инициализированное устройство."
            )
            return

        self.Manager.sync()

    def hide_to_tray(self):
        self.tray.show()
        self.hide()

    def show_window(self):
        self.show()
        self.raise_()

    def exit_app(self):
        self.tray.hide()
        QApplication.quit()



