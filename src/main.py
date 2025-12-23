if __name__ == "__main__":
    from PySide6.QtGui import QIcon
    from GUI.MainWindow import QApplication, SyncApp
    import threading
    from pathlib import Path
    import sys

    launch_dir = Path(sys.argv[0]).resolve().parent
    config = launch_dir / "config" / "config.json"
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images.jpg"))
    window = SyncApp(config.as_posix())
    window.show()
    t = threading.Thread(target=window.Validator.usb_monitor, daemon=True)
    t.start()
    sys.exit(app.exec())
