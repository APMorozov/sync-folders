from DirHistory import DirHistory

from pathlib import Path


class Comparer:
    """Класс реализующий логику сравнения двух директорий """

    @staticmethod
    def take_differences(pc_set_of_files: set, flash_set_of_files: set) -> tuple[set[Path], set[Path]]:
        """
        Находит различия между директориями
        :param pc_set_of_files: файлы в директори на пк
        :param flash_set_of_files: файлы в директори на флэшке
        :return: файлы которых нет на пк, файлы которых нет на флэшке
        """
        no_on_pc = flash_set_of_files - pc_set_of_files
        no_on_flash = pc_set_of_files - flash_set_of_files
        return no_on_pc, no_on_flash

    @staticmethod
    def resolve_sync_actions(differences: set[Path], history: DirHistory) -> set[Path]:
        """
        Возвращает файлы которые нужно копировать на носитель(пк или флэшка)
        :param differences: файлы которых нет на носителе
        :param history: класс реализующий  логику ведения файловой истории на носителе
        :return: файлы которые нужно копировать
        """
        must_be_sync = set()
        for difference in differences:
            if not history.is_deleted(difference):
                must_be_sync.add(difference)
        return must_be_sync
