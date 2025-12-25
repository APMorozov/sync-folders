from trial_version import calc_hash
from utils.file_work import write_json

import hashlib
from pathlib import Path
import sys
import time


def get_secret(path_to_exe: Path):
    """
    Вычисляет хэш exe файла
    :param path_to_exe:
    :return:
    """
    with open(path_to_exe, "rb") as f:
        chunk = f.read(4096)
    return hashlib.sha256(chunk).hexdigest()


def init_trial(launch_dir: Path, exe_name: str):
    """
    Создание файла .trial.json
    :param launch_dir: путь до директории с exe файлом
    :param exe_name: название exe файла
    :return:
    """
    now = time.time()
    trial_file = launch_dir / "config" / ".trial.json"
    exe_file = launch_dir / exe_name
    secret = get_secret(exe_file)

    if trial_file.exists():
        return

    data = {
        "first_run": now,
        "last_run": now,
        "hash": calc_hash(now, now, secret)
    }

    write_json(trial_file.as_posix(), data)


if __name__ == "__main__":
    launch_dir = Path("C:\\Users\\moroz\\OneDrive\\Desktop\\3-kurs\\Kursovaia\\sync-folders\\src\\dist")
    exe_name = "trial_version.exe"
    init_trial(launch_dir, exe_name)
