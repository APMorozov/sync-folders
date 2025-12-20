from src.core.StateManager import StateManager
from src.utils.hash_compute import hash_file_sha1
from pathlib import Path
from enum import Enum, auto


class Action(Enum):
    COPY_TO_PC = auto()
    COPY_TO_FLASH = auto()
    DELETE_PC = auto()
    DELETE_FLASH = auto()
    CONFLICT = auto()



class SyncPlanner:

    def get_update_action(self, files, state: StateManager, pc_folder: Path):
        plan = {}
        for f in files:
            is_delete, deleted_at = state.is_deleted(f.__str__())
            if is_delete:
                continue
            pc_abs_path = pc_folder / f
            flash_abs_path = state.flash_folder / f
            if hash_file_sha1(pc_abs_path.as_posix()) == hash_file_sha1(flash_abs_path.as_posix()):
                continue

            pc_abs_path = pc_folder / f
            flash_abs_path = state.flash_folder / f
            pc_changed = hash_file_sha1(pc_abs_path.as_posix()) != state.state["files"]["hash"]
            fl_changed = hash_file_sha1(flash_abs_path.as_posix()) != state.state["files"]["hash"]

            if pc_changed and fl_changed:
                plan[f] = Action.CONFLICT
            elif pc_changed:
                plan[f] = Action.COPY_TO_FLASH
            elif fl_changed:
                plan[f] = Action.COPY_TO_PC
        return plan

    @staticmethod
    def get_sync_plan_for_btn_action(no_on_pc: set[Path], no_on_flash: set[Path], state: StateManager,
                                        pc_folder: Path) -> dict[Path, Action]:
        plan = {}
        all_files = set(no_on_pc) | set(no_on_flash)
        for f in all_files:
            pc_f = f in no_on_pc
            fl_f = f in no_on_flash
            is_delete, deleted_at = state.is_deleted(f.__str__())
            state_files = state.state["files"].keys()
            #удалить
            if fl_f and not pc_f:
                if f.__str__() not in state_files:
                    plan[f] = Action.CONFLICT
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
    def get_sync_plan_for_attach_action(no_on_pc: set[Path], no_on_flash: set[Path], state: StateManager, pc_folder: Path) -> dict:
        plan = {}
        all_files = set(no_on_pc) | set(no_on_flash)
        for f in all_files:
            pc_f = f in no_on_pc
            fl_f = f in no_on_flash
            is_delete, deleted_at = state.is_deleted(f.__str__())

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
                elif pc_changed:
                    plan[f] = Action.COPY_TO_FLASH
                elif fl_changed:
                    plan[f] = Action.COPY_TO_PC

        return plan
