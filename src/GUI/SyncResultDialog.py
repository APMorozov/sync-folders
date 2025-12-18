from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QTabWidget, QListWidgetItem, QWidget, QScrollArea
)
from PySide6.QtCore import Qt
from pathlib import Path

class SyncResultDialog(QDialog):
    def __init__(self, errors: list, copied_files: list, updated_files: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результаты синхронизации")
        self.resize(600, 400)
        self.errors = errors
        self.copied_files = copied_files
        self.updated_files = updated_files

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Создаём вкладки
        tabs = QTabWidget()
        tabs.addTab(self.create_list_tab(self.errors, "Ошибки"), "Ошибки")
        tabs.addTab(self.create_list_tab(self.copied_files, "Скопированные файлы"), "Скопированные")
        tabs.addTab(self.create_list_tab(self.updated_files, "Обновлённые файлы"), "Обновлённые")

        layout.addWidget(tabs)

        # Кнопка закрыть
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def create_list_tab(self, items, title=""):
        """
        Создаёт вкладку со списком
        :param items: список объектов SyncInfo
        :param title: заголовок (необязательно)
        """
        widget = QWidget()
        v_layout = QVBoxLayout(widget)

        list_widget = QListWidget()
        for item in items:
            if hasattr(item, "file") and hasattr(item, "reason"):
                text = f"{item.file} — {item.reason}"
            else:
                text = str(item)
            list_widget.addItem(QListWidgetItem(text))

        v_layout.addWidget(list_widget)
        return widget
