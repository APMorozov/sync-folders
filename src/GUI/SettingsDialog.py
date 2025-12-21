from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFileDialog, QMessageBox
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
        btn_remove = QPushButton("Удалить выбранную")
        btn_add.clicked.connect(self.add_ignore_folder)
        btn_remove.clicked.connect(self.remove_ignore_folder)

        row_ignore = QHBoxLayout()
        row_ignore.addWidget(btn_add)
        row_ignore.addWidget(btn_remove)

        layout.addWidget(self.ignore_list)
        layout.addLayout(row_ignore)

        btn_apply = QPushButton("Применить")
        btn_cancel = QPushButton("Отмена")

        btn_apply.clicked.connect(self.on_apply)
        btn_cancel.clicked.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_cancel)
        bottom.addWidget(btn_apply)

        layout.addLayout(bottom)

    def set_data_from_config(self, data: dict) -> None:
        """
        Установка информации из конфига
        :param data: инфомация
        :return:
        """
        self.pc_folder.setText(data.get("pc_folder", ""))

        flash = data.get("flash_folder", "")
        if flash:
            self.flash_folder.setText(self.extract_root(flash))

        self.ignore_list.clear()
        for folder in data.get("ignore_files", []):
            self.ignore_list.addItem(folder)

    def get_config(self) -> dict:
        """
        Создание обновленного конфига из полей класса
        :return: Новый конфиг
        """
        return {
            "pc_folder": self.pc_folder.text(),
            "flash_folder": self.flash_folder.text(),
            "ignore_files": self.transform_path_ignore_folders()
        }

    def on_apply(self) -> None:
        """
        Логика кнопки принять
        :return:
        """
        if not self.validate():
            return
        self.accept()

    def validate(self) -> bool:
        """
        Валидация информации введенной пользователем
        :return: Подходит или нет
        """
        if not self.pc_folder.text().strip():
            self.error("Не выбран путь к папке на компьютере")
            return False

        if not self.flash_folder.text().strip():
            self.error("Не выбран путь к флэшке")
            return False

        if not self.is_root_path(self.flash_folder.text()):
            self.error(
                "Путь к флэшке должен указывать на КОРЕНЬ устройства\n\n"
                "Пример:\nE:\\"
            )
            return False

        return True

    def error(self, text: str) -> None:
        """
        Ошибка
        :param text:
        :return:
        """
        QMessageBox.warning(self, "Ошибка", text)

    @staticmethod
    def extract_root(path: str) -> str:
        """
        Извелечение чистого корня флэшки
        :param path:
        :return:
        """
        p = Path(path)
        return p.anchor or p.parts[0]

    @staticmethod
    def is_root_path(path: str) -> bool:
        """Проверка корень файловой системы или нет"""
        p = Path(path)
        return p.parent == p

    def choose_pc_folder(self) -> None:
        """
        Выбор папки на пк
        :return:
        """
        folder = QFileDialog.getExistingDirectory(self, "Выбор исходной папки")
        if folder:
            self.pc_folder.setText(folder)

    def choose_flash_folder(self) -> None:
        """
        Выбор папки на флэшке
        :return:
        """
        folder = QFileDialog.getExistingDirectory(self, "Выбор корня флэшки")
        if folder:
            self.flash_folder.setText(self.extract_root(folder))

    def add_ignore_folder(self) -> None:
        """
        Добавление игнор папок
        :return:
        """
        if not self.pc_folder.text():
            self.error("Сначала выберите папку для синхронизации на компьютере")
            return

        base_path = Path(self.pc_folder.text())
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку для игнорирования", str(base_path)
        )

        if not folder:
            return

        folder_path = Path(folder)


        try:
            relative = folder_path.relative_to(base_path)
        except ValueError:
            self.error("Игнорируемая папка должна находиться внутри папки синхронизации")
            return

        relative_str = relative.as_posix()

        if relative.parts[0] == ".sync":
            self.error("Папку .sync нельзя добавлять в игнорируемые")
            return

        existing = [
            self.ignore_list.item(i).text()
            for i in range(self.ignore_list.count())
        ]

        if relative_str in existing:
            self.error(f"Папка «{relative_str}» уже находится в игнорируемых")
            return

        self.ignore_list.addItem(relative_str)

    def remove_ignore_folder(self) -> None:
        """
        Удаление игнор папок
        :return:
        """
        for item in self.ignore_list.selectedItems():
            if Path(item.text()).name == ".sync":
                self.error("Папку .sync нельзя удалить из игнорируемых")
                return
            self.ignore_list.takeItem(self.ignore_list.row(item))

    def transform_path_ignore_folders(self) -> list[str]:
        """
        Обработка игнор папок
        :return: переработаные игнор папки
        """

        return [
            self.ignore_list.item(i).text()
            for i in range(self.ignore_list.count())
        ]
