import shutil


class Synchronizer:
    def __init__(self, pc_folder, flash_folder):
        self.pc_folder = pc_folder
        self.flash_folder = flash_folder

    def synchronize(self, no_on_pc, no_on_flash):
        for file in no_on_pc:
            path = self.pc_folder / file
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.flash_folder / file, path)

        for file in no_on_flash:
            path = self.flash_folder / file
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.pc_folder / file, path,)
