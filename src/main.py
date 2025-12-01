from SyncManager import SyncManager
from file_work import read_json
import shutil
#from GUI.App import App
import os

from DirHistory import DirHistory
from pathlib import Path

if __name__ == "__main__":
    config = read_json("C:\\Users\\moroz\\OneDrive\\Desktop\\3-kurs\\Kursovaia\\sync-folders\\src\\config.json")
    #keys = list(config.keys())
    #print("Settings:", config[keys[0]])
    Manager = SyncManager(config)
    Manager.go()


