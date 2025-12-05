from GUI.MainWindow import QApplication, SyncApp

import sys


if __name__ == "__main__":
    config = "C:\\Users\\moroz\\OneDrive\\Desktop\\3-kurs\\Kursovaia\\sync-folders\\src\\config.json"
    app = QApplication(sys.argv)
    window = SyncApp(config)
    window.show()
    sys.exit(app.exec())


