from PySide6.QtCore import Signal, QObject
import time


class EventBus(QObject):
    usb_detected = Signal()



    def usb_monitor(self):
        known = set()

        while True:
            import psutil
            drives = {d.device for d in psutil.disk_partitions() if "removable" in d.opts}

            new_drives = drives - known
            if new_drives:
                print("USB detected:", new_drives)
                self.usb_detected.emit()

            known = drives
            time.sleep(1)