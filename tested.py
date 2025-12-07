import sys
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, QObject



class EventBus(QObject):
    usb_detected = Signal()



event_bus = EventBus()

def usb_monitor():
    known = set()

    while True:
        import psutil
        drives = {d.device for d in psutil.disk_partitions() if "removable" in d.opts}

        # если появился новый
        new_drives = drives - known
        if new_drives:
            print("USB detected:", new_drives)
            event_bus.usb_detected.emit()

        known = drives
        time.sleep(1)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("USB Sync Settings")
        btn = QPushButton("Свернуть в трей", self)
        btn.clicked.connect(self.hide_to_tray)
        self.setCentralWidget(btn)

        # Tray icon
        self.tray = QSystemTrayIcon(QIcon("images.jpg"), self)
        tray_menu = QMenu()
        tray_menu.addAction("Открыть", self.show_window)
        tray_menu.addAction("Выход", self.exit_app)
        self.tray.setContextMenu(tray_menu)

        event_bus.usb_detected.connect(self.ask_password)

    def hide_to_tray(self):
        self.tray.show()
        self.hide()

    def show_window(self):
        self.show()
        self.raise_()

    def ask_password(self):
        QMessageBox.information(self, "USB", "Обнаружено устройство. Введите пароль.")

    def exit_app(self):
        self.tray.hide()
        QApplication.quit()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    t = threading.Thread(target=usb_monitor, daemon=True)
    t.start()

    sys.exit(app.exec())
