if __name__ == "__main__":
    from GUI.MainWindow import QApplication, SyncApp
    from src.utils.file_work import read_json
    import threading
    from pathlib import Path
    import sys

    launch_dir = Path(sys.argv[0]).resolve().parent
    print(launch_dir)
    config = launch_dir / "config" / "config.json"
    app = QApplication(sys.argv)
    window = SyncApp(config.as_posix())
    window.show()
    t = threading.Thread(target=window.Bus.usb_monitor, daemon=True)
    t.start()
    sys.exit(app.exec())
