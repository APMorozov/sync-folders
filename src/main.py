from SyncManager import SyncManager
from file_work import read_json
import os

if __name__ == "__main__":
    config = read_json("C:\\Users\\moroz\\OneDrive\\Desktop\\3-kurs\\Kursovaia\\sync-folders\\src\\config.json")
    print("Settings:", config)
    Manager = SyncManager(config)
    Manager.check_sync()
