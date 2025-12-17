from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFileDialog
)
from pathlib import Path


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(520, 400)

        self._config = config.copy()
        self.init_ui()
        self.set_data_from_config(self._config)

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Путь до папки на компьютере"))
        self.pc_folder = QLineEdit()
        btn_pc = QPushButton("Выбрать…")
        btn_pc.clicked.connect(self.choose_pc_folder)

        row_pc = QHBoxLayout()
        row_pc.addWidget(self.pc_folder)
        row_pc.addWidget(btn_pc)
        layout.addLayout(row_pc)

        layout.addWidget(QLabel("Путь до корня флэшки"))
        self.flash_folder = QLineEdit()
        btn_flash = QPushButton("Выбрать…")
        btn_flash.clicked.connect(self.choose_flash_folder)

        row_flash = QHBoxLayout()
        row_flash.addWidget(self.flash_folder)
        row_flash.addWidget(btn_flash)
        layout.addLayout(row_flash)

        layout.addWidget(QLabel("Игнорируемые папки"))
        self.ignore_list = QListWidget()

        btn_add = QPushButton("Добавить папку…")
        btn_add.clicked.connect(self.add_ignore_folder)
        btn_remove = QPushButton("Удалить выбранную")
        btn_remove.clicked.connect(self.remove_ignore_folder)

        row_ignore = QHBoxLayout()
        row_ignore.addWidget(btn_add)
        row_ignore.addWidget(btn_remove)

        layout.addWidget(self.ignore_list)
        layout.addLayout(row_ignore)

        btn_apply = QPushButton("Применить")
        btn_cancel = QPushButton("Отмена")

        btn_apply.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_cancel)
        bottom.addWidget(btn_apply)

        layout.addLayout(bottom)

    def set_data_from_config(self, data: dict):
        self.pc_folder.setText(data.get("pc_folder", ""))
        self.flash_folder.setText(data.get("flash_folder", ""))
        self.ignore_list.clear()
        for folder in data.get("ignore_files", []):
            self.ignore_list.addItem(folder)

    def choose_pc_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбор исходной папки")
        if folder:
            self.pc_folder.setText(folder)

    def choose_flash_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбор целевой папки")
        if folder:
            self.flash_folder.setText(folder)

    def add_ignore_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для игнорирования")
        if folder:
            self.ignore_list.addItem(folder)

    def remove_ignore_folder(self):
        for item in self.ignore_list.selectedItems():
            self.ignore_list.takeItem(self.ignore_list.row(item))

    def transform_path_ignore_folders(self) -> list[str]:
        """ Приводит пути взятые из интерфейса к виду с которым работает ядро приложения :return: """

        ignore_array = [self.ignore_list.item(i).text() for i in range(self.ignore_list.count())]
        transformed_folders = [Path(path).parts[-1] for path in ignore_array]
        return transformed_folders

    def get_config(self) -> dict:
        return {
            "pc_folder": self.pc_folder.text(),
            "flash_folder": self.flash_folder.text(),
            "ignore_files": self.transform_path_ignore_folders()
        }
