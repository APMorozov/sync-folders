class Comparer:

    @staticmethod
    def take_differences(pc_set_of_files: set,flash_set_of_files: set):
        no_on_pc = flash_set_of_files - pc_set_of_files
        no_on_flash = pc_set_of_files - flash_set_of_files
        return no_on_pc, no_on_flash

