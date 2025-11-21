class Comparer:
    @staticmethod
    def compare_dirs(pc_list_of_files, flash_list_of_files):
        no_on_pc = []
        for different in flash_list_of_files - pc_list_of_files:
            no_on_pc.append(different)

        no_on_flash = []
        for different in pc_list_of_files - flash_list_of_files:
            no_on_flash.append(different)

        return no_on_pc, no_on_flash
