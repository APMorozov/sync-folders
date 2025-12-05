import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QComboBox, QLineEdit
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QTimer
from pathlib import Path

from src.core.SyncManager import SyncManager
from src.utils.file_work import write_json, read_json


class SyncApp(QWidget):

    def set_data_from_config(self, data):
        self.pc_folder.setText(data.get("pc_folder", ""))
        self.flash_folder.setText(data.get("flash_folder", ""))

        self.interval = data.get("sync_interval_sec", 360)

        mapping = {
            360: 0,
            3000: 1,
            6000: 2,
            86400: 3,
            15: 4
        }
        self.freq_combo.setCurrentIndex(mapping.get(self.interval, 0))

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
        self.Manager = SyncManager(read_json(self.path_to_config))
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)

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

        self.pc_folder = QLineEdit()
        self.pc_folder.setPlaceholderText("Выберите исходную папку...")
        btn_src = QPushButton("Выбрать…")
        btn_src.clicked.connect(self.choose_pc_folder)

        row_src = QHBoxLayout()
        row_src.addWidget(self.pc_folder)
        row_src.addWidget(btn_src)

        self.flash_folder = QLineEdit()
        self.flash_folder.setPlaceholderText("Выберите целевую папку...")
        btn_dst = QPushButton("Выбрать…")
        btn_dst.clicked.connect(self.choose_flash_folder)

        row_dst = QHBoxLayout()
        row_dst.addWidget(self.flash_folder)
        row_dst.addWidget(btn_dst)

        freq_label = QLabel("Частота синхронизации:")
        self.freq_combo = QComboBox()
        self.freq_combo.addItems([
            "Каждые 5 минут",
            "Каждые 30 минут",
            "Каждый час",
            "Каждый день",
            "Каждые 15 сек"
        ])

        row_freq = QHBoxLayout()
        row_freq.addWidget(freq_label)
        row_freq.addWidget(self.freq_combo)

        ignore_label = QLabel("Игнорируемые папки:")

        self.ignore_list = QListWidget()

        btn_add_ignore = QPushButton("Добавить папку…")
        btn_add_ignore.clicked.connect(self.add_ignore_folder)

        btn_remove_ignore = QPushButton("Удалить выбранную")
        btn_remove_ignore.clicked.connect(self.remove_ignore_folder)

        row_ignore_btns = QHBoxLayout()
        row_ignore_btns.addWidget(btn_add_ignore)
        row_ignore_btns.addWidget(btn_remove_ignore)

        btn_sync = QPushButton("Синхронизировать")
        btn_sync.setFixedHeight(40)
        btn_sync.clicked.connect(self.sync_action)

        main_layout.addLayout(row_src)
        main_layout.addLayout(row_dst)
        main_layout.addLayout(row_freq)

        main_layout.addWidget(ignore_label)
        main_layout.addWidget(self.ignore_list)
        main_layout.addLayout(row_ignore_btns)

        main_layout.addWidget(btn_sync)

        self.setLayout(main_layout)

    def take_sync_interval(self):
        """
        Подтягивает выбранное пользователем время из интерфейса
        :return: интервал синхронизации: сек
        """
        match self.freq_combo.currentIndex():
            case 0:
                return 360 #Вынести в константы
            case 1:
                return 3000
            case 2:
                return 6000
            case 3:
                return 86400
            case 4:
                return 15

    def transform_path_ignore_folders(self) -> list[str]:
        """
        Приводит пути взятые из интерфейса к виду с которым работает ядро приложения
        :return:
        """
        ignore_array = [self.ignore_list.item(i).text() for i in range(self.ignore_list.count())]
        transformed_folders = [Path(path).parts[-1] for path in ignore_array ]
        return transformed_folders

    def update_settings_file(self):
        """
        Собирает и записывает в конфиг все данные введенные пользователем в интерфейс
        :return:
        """
        data = {"pc_folder": self.pc_folder.text(), "flash_folder": self.flash_folder.text(),
                "ignore_files": self.transform_path_ignore_folders(), "sync_interval_sec": self.take_sync_interval()}
        print("Update config:", data)
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
        Синхронизация происходящая каждый интервал
        :return:
        """
        self.Manager.go()
        self.sync_timer.start(self.interval * 1000)

    def sync_action(self):
        """
        Начальная синхронизация, происходящая при нажатии кнопки
        :return:
        """
        self.update_settings_file()
        self.Manager.start_sync()
        self.auto_sync()


