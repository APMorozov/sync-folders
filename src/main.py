from GUI.MainWindow import QApplication, SyncApp
from src.utils.file_work import read_json
from src.core.SyncManager import SyncManager
from src.core.EventBus import EventBus

import threading
import sys


if __name__ == "__main__":
    config = "C:\\Users\\moroz\\OneDrive\\Desktop\\3-kurs\\Kursovaia\\sync-folders\\src\\config.json"
    data = read_json(config)
    app = QApplication(sys.argv)
    window = SyncApp(config)
    window.show()
    t = threading.Thread(target=window.Bus.usb_monitor, daemon=True)
    t.start()
    sys.exit(app.exec())

