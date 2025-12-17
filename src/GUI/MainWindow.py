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

    def set_data_from_config(self, data: dict):
        """
        Устанавливает данные из файла настроек
        :param data: данные файла настроек
        :return:
        """
        self.pc_folder.setText(data.get("pc_folder", ""))
        self.flash_folder.setText(data.get("flash_folder", ""))
        self.ignore_list.clear()
        for folder in data.get("ignore_files", []):
            self.ignore_list.addItem(folder)

    def __init__(self, path_to_config: str):
        """

        :param path_to_config: абсолютный путь к конфигу
        """
        super().__init__()
        self.init_ui()
        self.path_to_config = path_to_config
        self.set_data_from_config(read_json(self.path_to_config))

        self.tray = QSystemTrayIcon(QIcon("images.jpg"), self)
        tray_menu = QMenu()
        tray_menu.addAction("Открыть", self.show_window)
        tray_menu.addAction("Выход", self.exit_app)
        self.tray.setContextMenu(tray_menu)
        self.Bus = EventBus(read_json(path_to_config)["pc_folder"])
        self.Bus.usb_detected.connect(self.ask_password)

    def init_ui(self):
        """
        Инициация интерфейса
        :return:
        """
        self.setWindowTitle("Cинхронизатор файлов")
        self.resize(520, 400)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#F2F2F7"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#E6E6EB"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#C7D8EA"))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ---- Путь к папке на компьютере ----
        pc_label = QLabel("Путь до папки на компьютере")

        self.pc_folder = QLineEdit()
        self.pc_folder.setPlaceholderText("Выберите исходную папку...")
        btn_src = QPushButton("Выбрать…")
        btn_src.clicked.connect(self.choose_pc_folder)

        row_src = QHBoxLayout()
        row_src.addWidget(self.pc_folder)
        row_src.addWidget(btn_src)

        # ---- Путь к папке на флэшке ----
        flash_label = QLabel("Путь до папки на флэшке")

        self.flash_folder = QLineEdit()
        self.flash_folder.setPlaceholderText("Выберите целевую папку...")
        btn_dst = QPushButton("Выбрать…")
        btn_dst.clicked.connect(self.choose_flash_folder)

        row_dst = QHBoxLayout()
        row_dst.addWidget(self.flash_folder)
        row_dst.addWidget(btn_dst)

        # ---- Игнорируемые папки ----
        ignore_label = QLabel("Игнорируемые папки:")
        self.ignore_list = QListWidget()

        btn_add_ignore = QPushButton("Добавить папку…")
        btn_add_ignore.clicked.connect(self.add_ignore_folder)

        btn_remove_ignore = QPushButton("Удалить выбранную")
        btn_remove_ignore.clicked.connect(self.remove_ignore_folder)

        row_ignore_btns = QHBoxLayout()
        row_ignore_btns.addWidget(btn_add_ignore)
        row_ignore_btns.addWidget(btn_remove_ignore)

        # ---- Нижние кнопки ----
        btn_tray = QPushButton("Свернуть в трэй")
        btn_tray.clicked.connect(self.hide_to_tray)

        btn_sync = QPushButton("Синхронизировать")
        btn_sync.clicked.connect(self.sync_action)

        btn_update_cfg = QPushButton("Обновить файл настроек")
        btn_update_cfg.clicked.connect(self.update_settings_file)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addWidget(btn_tray)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(btn_update_cfg)
        bottom_buttons.addWidget(btn_sync)

        # ---- Сборка интерфейса ----
        main_layout.addWidget(pc_label)
        main_layout.addLayout(row_src)

        main_layout.addWidget(flash_label)
        main_layout.addLayout(row_dst)

        main_layout.addWidget(ignore_label)
        main_layout.addWidget(self.ignore_list)
        main_layout.addLayout(row_ignore_btns)

        main_layout.addLayout(bottom_buttons)

        self.setLayout(main_layout)

    def hide_to_tray(self):
        """
        Убрать в трей
        :return:
        """
        self.tray.show()
        self.hide()

    def show_window(self):
        """
        Показать окно
        :return:
        """
        self.show()
        self.raise_()

    def update_flash_path(self, path_flash: Path):
        data = {"pc_folder": self.pc_folder.text(), "flash_folder": path_flash.__str__(),
                "ignore_files": self.transform_path_ignore_folders()}
        write_json(self.path_to_config, data)

    def ask_password(self, path_flash: Path):
        """
        Запрос пароля при обнаружении флэшки
        :return:
        """
        QMessageBox.information(self, "USB", "Обнаружено устройство. Введите пароль.")
        self.set_data_from_config(read_json(self.path_to_config))
        self.update_flash_path(path_flash)
        self.Manager = SyncManager(read_json(self.path_to_config)) 
        self.auto_sync()

    def exit_app(self):
        """
        Закрытие приложения из Tray
        :return:
        """
        self.tray.hide()
        QApplication.quit()

    def transform_path_ignore_folders(self) -> list[str]:
        """
        Приводит пути взятые из интерфейса к виду с которым работает ядро приложения
        :return:
        """
        ignore_array = [self.ignore_list.item(i).text() for i in range(self.ignore_list.count())]
        transformed_folders = [Path(path).parts[-1] for path in ignore_array]
        return transformed_folders

    def update_settings_file(self):
        """
        Собирает и записывает в конфиг все данные введенные пользователем в интерфейс
        :return:
        """
        data = {"pc_folder": self.pc_folder.text(), "flash_folder": self.flash_folder.text(),
                "ignore_files": self.transform_path_ignore_folders()}
        write_json(self.path_to_config, data)

    def choose_pc_folder(self):
        """
        Выбор папки и отображение ее в интерфейсе
        :return:
        """
        folder = QFileDialog.getExistingDirectory(self, "Выбор исходной папки")
        if folder:
            self.pc_folder.setText(folder)

    def choose_flash_folder(self):
        """
        Выбор папки и отображение ее в интерфейсе
        :return:
        """
        folder = QFileDialog.getExistingDirectory(self, "Выбор целевой папки")
        if folder:
            self.flash_folder.setText(folder)

    def add_ignore_folder(self):
        """
        Выбор игнор папки и отображение ее в интерфейсе
        :return:
        """
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для игнорирования")
        if folder:
            self.ignore_list.addItem(folder)

    def remove_ignore_folder(self):
        """
        Удаление игнор папки и отображение этого в интерфейсе
        :return:
        """
        for item in self.ignore_list.selectedItems():
            self.ignore_list.takeItem(self.ignore_list.row(item))

    def auto_sync(self):
        """
        Синхронизация происходящая при обнаружении флэшки
        :return:
        """
        self.Manager.sync()

    def sync_action(self):
        """
        Начальная синхронизация, происходящая при нажатии кнопки
        :return:
        """
        self.update_settings_file()
        self.Manager = SyncManager(read_json(self.path_to_config))
        self.auto_sync()


