from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QListWidget
)
from pathlib import Path


class AttachFlashDialog(QDialog):
    """Класс реализующий логику настройки подключения уже инициализированной флэшки"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Присоединить флэшку")
        self.resize(480, 320)

        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Папка на флэшке (с .sync)"))
        self.flash_folder = QLineEdit()
        btn_flash = QPushButton("Выбрать…")
        btn_flash.clicked.connect(self.choose_flash)

        row_flash = QHBoxLayout()
        row_flash.addWidget(self.flash_folder)
        row_flash.addWidget(btn_flash)
        layout.addLayout(row_flash)

        layout.addWidget(QLabel("Папка на компьютере"))
        self.pc_folder = QLineEdit()
        btn_pc = QPushButton("Выбрать…")
        btn_pc.clicked.connect(self.choose_pc)

        row_pc = QHBoxLayout()
        row_pc.addWidget(self.pc_folder)
        row_pc.addWidget(btn_pc)
        layout.addLayout(row_pc)


        layout.addWidget(QLabel("Игнорируемые папки"))
        self.ignore_list = QListWidget()
        self.ignore_list.addItem(".sync")
        layout.addWidget(self.ignore_list)

        btn_add = QPushButton("Добавить папку…")
        btn_remove = QPushButton("Удалить выбранную")

        btn_add.clicked.connect(self.add_ignore_folder)
        btn_remove.clicked.connect(self.remove_ignore_folder)

        row_ignore = QHBoxLayout()
        row_ignore.addWidget(btn_add)
        row_ignore.addWidget(btn_remove)
        layout.addLayout(row_ignore)

        btn_apply = QPushButton("Применить")
        btn_cancel = QPushButton("Отмена")

        btn_apply.clicked.connect(self.validate_and_accept)
        btn_cancel.clicked.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_cancel)
        bottom.addWidget(btn_apply)

        layout.addLayout(bottom)

    def choose_flash(self) -> None:
        """
        Выбор пути для флэшки
        :return:
        """

        folder = QFileDialog.getExistingDirectory(self, "Выберите папку на флэшке")
        if folder:
            self.flash_folder.setText(folder)

    def choose_pc(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку на компьютере")
        if folder:
            self.pc_folder.setText(folder)

    def add_ignore_folder(self) -> None:
        """
        Добавление игнорируемых папок
        :return:
        """
        pc_root = self.pc_folder.text()
        if not pc_root:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Сначала выберите папку синхронизации на ПК."
            )
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для игнорирования",
            pc_root
        )

        if not folder:
            return

        try:
            relative = Path(folder).relative_to(Path(pc_root))
        except ValueError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Игнорируемая папка должна находиться внутри папки синхронизации."
            )
            return

        rel_str = relative.as_posix()

        existing = [
            self.ignore_list.item(i).text()
            for i in range(self.ignore_list.count())
        ]

        if rel_str in existing:
            QMessageBox.information(
                self,
                "Информация",
                "Эта папка уже находится в списке игнорируемых."
            )
            return

        self.ignore_list.addItem(rel_str)

    def remove_ignore_folder(self) -> None:
        """
        Удаление игнорируемых файлов
        :return:
        """
        for item in self.ignore_list.selectedItems():
            if item.text() == ".sync":
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Папку .sync нельзя удалить из игнорируемых."
                )
                continue

            self.ignore_list.takeItem(self.ignore_list.row(item))

    def validate_and_accept(self) -> None:
        """
        Валадация введенных данных
        :return:
        """
        flash = Path(self.flash_folder.text())
        pc = Path(self.pc_folder.text())

        if not flash.exists():
            QMessageBox.warning(self, "Ошибка", "Путь к флэшке не выбран.")
            return

        if not (flash / ".sync").exists():
            QMessageBox.warning(
                self,
                "Ошибка",
                "В выбранной папке на флэшке нет каталога .sync.\n\n"
                "Это устройство не инициализировано."
            )
            return

        if not (flash / ".sync" / "code").exists():
            QMessageBox.warning(
                self,
                "Ошибка",
                "В выбранной папке на флжшке нет файла code в каталоге .sync\n\n"
                "Это устройство не инициализировано."
            )
            return

        if not pc.exists():
            QMessageBox.warning(self, "Ошибка", "Путь к папке на ПК не выбран.")
            return
        if pc.name != flash.name:
            QMessageBox.warning(self, "Ошибка", "Названия папок на флэшке и пк отличаются.")
            return

        self.accept()

    def get_result(self) -> dict:
        """
        Изменненые данные конфига
        :return:
        """

        ignore_files = [
            self.ignore_list.item(i).text()
            for i in range(self.ignore_list.count())
        ]

        return {
            "flash_folder": self.flash_folder.text(),
            "pc_folder": self.pc_folder.text(),
            "ignore_files": ignore_files
        }
