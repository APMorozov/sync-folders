from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from utils.file_work import write_json, read_json


import hashlib
import json
import sys
import time


def get_secret():
    """
    Вычисляет хэш exe файла
    :return:
    """
    path = Path(sys.executable)
    with open(path, "rb") as f:
        chunk = f.read(4096)
    return hashlib.sha256(chunk).hexdigest()


def calc_hash(first_run: float, last_run: float, secret):
    """
    Вычисляет хэш на основе строки из 3 параметров
    :param first_run: время первого запуска
    :param last_run: время последнего запуска
    :param secret: секретные данные
    :return: Hash
    """
    s = f"{first_run}:{last_run}:{secret}"
    return hashlib.sha256(s.encode()).hexdigest()


def check_trial(launch_dir: Path, trial_days: float) -> bool:
    """
    Функция проверяющая не закончился ли пробный период
    :param launch_dir: директория запуска приложения
    :param trial_days: время работы пробной версии
    :return:
    """
    trial_file = launch_dir / "config" / ".trial.json"
    now = time.time()
    secret = get_secret()

    try:
        if not trial_file.exists():
            return False

        data = read_json(trial_file)

        first_run = data.get("first_run")
        last_run = data.get("last_run")
        saved_hash = data.get("hash")
        day_hours = 24
        count_min_or_sec = 60

        if not all([first_run, last_run, saved_hash]):
            return False

        if now < last_run:
            return False

        if saved_hash != calc_hash(first_run, last_run, secret):
            return False

        trial_period_sec = trial_days * day_hours * count_min_or_sec * count_min_or_sec

        if now - first_run > trial_period_sec:
            return False

        data["last_run"] = now
        data["hash"] = calc_hash(first_run, now, secret)

        write_json(trial_file, data)

        return True

    except Exception:
        return False


if __name__ == "__main__":
    from PySide6.QtGui import QIcon
    from GUI.MainWindow import QApplication, SyncApp
    import threading
    from pathlib import Path
    import sys

    launch_dir = Path(sys.argv[0]).resolve().parent

    app = QApplication(sys.argv)

    trial_days = 0.0011

    if not check_trial(launch_dir, trial_days):
        QMessageBox.critical(
            None,
            "Пробный период завершён",
            "Срок действия пробной версии программы истёк.\n\n"
            "Для продолжения работы требуется полная версия."
        )
        sys.exit(0)

    config = launch_dir / "config" / "config.json"

    app.setWindowIcon(QIcon("images.jpg"))
    window = SyncApp(config.as_posix())
    window.show()

    t = threading.Thread(target=window.Validator.usb_monitor, daemon=True)
    t.start()

    sys.exit(app.exec())