from enum import Enum, auto


class Action(Enum):
    COPY_TO_PC = auto()
    COPY_TO_FLASH = auto()
    DELETE_PC = auto()
    DELETE_FLASH = auto()
    CONFLICT = auto()


class SyncPlanner:

    @staticmethod
    def build(pc, flash, last) -> dict:
        plan = {}
        all_files = set(pc) | set(flash) | set(last)

        for f in all_files:
            pc_f = pc.get(f)
            fl_f = flash.get(f)
            old = last.get(f)

            if not old:
                if pc_f and not fl_f:
                    plan[f] = Action.COPY_TO_FLASH
                elif fl_f and not pc_f:
                    plan[f] = Action.COPY_TO_PC
                continue

            if old and not pc_f and fl_f:
                plan[f] = Action.DELETE_FLASH
                continue

            if old and not fl_f and pc_f:
                plan[f] = Action.DELETE_PC
                continue

            if pc_f and fl_f:
                if pc_f.hash == fl_f.hash:
                    continue

                pc_changed = pc_f.hash != old.hash
                fl_changed = fl_f.hash != old.hash

                if pc_changed and fl_changed:
                    plan[f] = Action.CONFLICT
                elif pc_changed:
                    plan[f] = Action.COPY_TO_FLASH
                elif fl_changed:
                    plan[f] = Action.COPY_TO_PC

        return plan
