from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QTabWidget, QListWidgetItem, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path


class SyncResultDialog(QDialog):
    # 🔥 сигнал: (SyncInfo, action: str)
    resolveRequested = Signal(object, str)

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

        self.tabs = QTabWidget()

        self.errors_tab, self.errors_list = self.create_errors_tab()
        self.tabs.addTab(self.errors_tab, "Ошибки")
        self.tabs.addTab(self.create_list_tab(self.copied_files), "Скопированные")
        self.tabs.addTab(self.create_list_tab(self.updated_files), "Обновлённые")

        layout.addWidget(self.tabs)

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    # ---------- Ошибки ----------
    def create_errors_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        list_widget = QListWidget()
        for info in self.errors:
            text = f"{info.file} — {info.reason}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, info)
            list_widget.addItem(item)

        btn_resolve = QPushButton("Решить ошибку")
        btn_resolve.clicked.connect(lambda: self.resolve_selected_error(list_widget))

        layout.addWidget(list_widget)
        layout.addWidget(btn_resolve)

        return widget, list_widget

    # ---------- Универсальная вкладка ----------
    def create_list_tab(self, items):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        list_widget = QListWidget()
        for item in items:
            list_widget.addItem(QListWidgetItem(str(item)))

        layout.addWidget(list_widget)
        return widget

    # ---------- Логика решения ----------
    def resolve_selected_error(self, list_widget: QListWidget):
        item = list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Выберите строку")
            return

        info = item.data(Qt.UserRole)
        reason = info.reason.lower()

        # ⚠️ конфликт
        if "конфликт" in reason:
            res = QMessageBox.question(
                self,
                "Конфликт",
                f"{info.file}\n\n"
                "Да — оставить версию ПК\n"
                "Нет — оставить версию флэшки",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if res == QMessageBox.Cancel:
                return

            action = "conflict" if res == QMessageBox.Yes else "use_flash"

        # ❓ неизвестный файл
        elif "не извест" in reason:
            res = QMessageBox.question(
                self,
                "Неизвестный файл на флэшке",
                f"{info.file}\n\nСинхронизировать?",
                QMessageBox.Yes | QMessageBox.No
            )
            action = "unknown" if res == QMessageBox.Yes else "keep"

        # ❌ другое
        else:
            QMessageBox.information(self, "Информация", "Для этой ошибки нет сценария")
            return

        # 🚀 сигнал
        self.resolveRequested.emit(info, action)

        row = list_widget.row(item)
        list_widget.takeItem(row)
