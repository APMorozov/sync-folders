from src.core.StateManager import StateManager
from src.utils.hash_compute import hash_file_sha1

from enum import Enum, auto
from pathlib import Path


class Action(Enum):
    """Класс действий во время синхронизациии"""
    COPY_TO_PC = auto()
    COPY_TO_FLASH = auto()
    DELETE_PC = auto()
    DELETE_FLASH = auto()
    CONFLICT = auto()
    UNKNOWN_FILE = auto()


class SyncPlanner:
    """Класс реализующий логику составления плана синхронизации"""
    @staticmethod
    def get_sync_plan_for_btn_action(pc_files: set[Path],
                                     flash_files: set[Path],
                                     state: StateManager,
                                     pc_folder: Path) -> dict[Path, Action]:
        """
        Составление плана при синхронизации путем нажатия кнопки
        :param pc_files: Файлы на пк
        :param flash_files: Файлы на флэшке
        :param state: Класс состояний
        :param pc_folder: путь до папки на пк
        :return: План синхронизации
        """
        plan = {}
        all_files = set(pc_files) | set(flash_files)
        for f in all_files:
            pc_f = f in pc_files
            fl_f = f in flash_files
            is_delete, deleted_at = state.is_deleted(f.as_posix())
            state_files = state.state["files"].keys()
            if fl_f and not pc_f:
                if f.as_posix() not in state_files:
                    plan[f] = Action.UNKNOWN_FILE
                else:
                    plan[f] = Action.DELETE_FLASH
            if not fl_f and pc_f:
                if is_delete:
                    if (pc_folder / f).stat().st_mtime < state.state["files"].get(f.as_posix(), {})["deleted_at"]:
                        plan[f] = Action.DELETE_PC
                        continue
                    else:
                        plan[f] = Action.COPY_TO_FLASH
                        continue
                else:
                    plan[f] = Action.COPY_TO_FLASH
                    continue
            if pc_f and fl_f:
                pc_abs_path = pc_folder / f
                flash_abs_path = state.flash_folder / f
                if hash_file_sha1(pc_abs_path.as_posix()) == hash_file_sha1(flash_abs_path.as_posix()):
                    continue

                pc_abs_path = pc_folder / f
                flash_abs_path = state.flash_folder / f
                pc_changed = hash_file_sha1(pc_abs_path.as_posix()) != state.state["files"].get(f.as_posix(), {})["hash"]
                fl_changed = hash_file_sha1(flash_abs_path.as_posix()) != state.state["files"].get(f.as_posix(), {})["hash"]

                if pc_changed and fl_changed:
                    plan[f] = Action.CONFLICT
                elif pc_changed:
                    plan[f] = Action.COPY_TO_FLASH
                elif fl_changed:
                    plan[f] = Action.COPY_TO_PC
        return plan

    @staticmethod
    def get_sync_plan_for_attach_action(pc_files: set[Path],
                                        flash_files: set[Path],
                                        state: StateManager,
                                        pc_folder: Path) -> dict[Path, Action]:
        """
        Составление плана при синхронизации путем подключения флэшки
        :param pc_files: Файлы на пк
        :param flash_files: Файлы на флэшке
        :param state: Класс состояний
        :param pc_folder: путь до папки на пк
        :return: План синхронизации
        """
        plan = {}
        all_files = set(pc_files) | set(flash_files)
        for f in all_files:
            pc_f = f in pc_files
            fl_f = f in flash_files
            is_delete, deleted_at = state.is_deleted(f.as_posix())

            if not is_delete:
                if pc_f and not fl_f:
                    plan[f] = Action.COPY_TO_FLASH
                    continue
                elif fl_f and not pc_f:
                    plan[f] = Action.COPY_TO_PC
                    continue

            if is_delete and not pc_f and fl_f:
                if (state.flash_folder / f).stat().st_mtime < state.state["files"].get(f.as_posix(), {})["deleted_at"]:
                    plan[f] = Action.DELETE_FLASH
                    continue
                else:
                    plan[f] = Action.COPY_TO_PC
                    continue

            if is_delete and not fl_f and pc_f:
                if (pc_folder / f).stat().st_mtime < state.state["files"].get(f.as_posix(), {})["deleted_at"]:
                    plan[f] = Action.DELETE_PC
                    continue
                else:
                    plan[f] = Action.COPY_TO_FLASH
                    continue

            if pc_f and fl_f:
                pc_abs_path = pc_folder / f
                flash_abs_path = state.flash_folder / f
                if hash_file_sha1(pc_abs_path.as_posix()) == hash_file_sha1(flash_abs_path.as_posix()):
                    continue

                pc_abs_path = pc_folder / f
                flash_abs_path = state.flash_folder / f
                pc_changed = hash_file_sha1(pc_abs_path.as_posix()) != state.state["files"].get(f.as_posix(), {})["hash"]
                fl_changed = hash_file_sha1(flash_abs_path.as_posix()) != state.state["files"].get(f.as_posix(), {})["hash"]

                if pc_changed and fl_changed:
                    plan[f] = Action.CONFLICT
                else:
                    pc_time_changed = pc_abs_path.stat().st_mtime
                    flash_time_changed = flash_abs_path.stat().st_mtime
                    if pc_time_changed > flash_time_changed:
                        plan[f] = Action.COPY_TO_FLASH
                    else:
                        plan[f] = Action.COPY_TO_PC

        return plan
