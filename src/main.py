from GUI.MainWindow import QApplication, SyncApp
from src.utils.file_work import read_json
from src.core.SyncManager import SyncManager
import sys


if __name__ == "__main__":
    config = "C:\\Users\\moroz\\OneDrive\\Desktop\\3-kurs\\Kursovaia\\sync-folders\\src\\config.json"
    data = read_json(config)
    Manager = SyncManager(data)
    Manager.sync()

