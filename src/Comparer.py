from DirHistory import DirHistory


class Comparer:

    @staticmethod
    def take_differences(pc_set_of_files: set, flash_set_of_files: set):
        no_on_pc = flash_set_of_files - pc_set_of_files
        no_on_flash = pc_set_of_files - flash_set_of_files
        return no_on_pc, no_on_flash

    @staticmethod
    def resolve_sync_actions(differences: set, history: DirHistory):
        must_be_sync = []
        for difference in differences:
            if not history.is_deleted(difference):
                must_be_sync.append(difference)
        return must_be_sync
