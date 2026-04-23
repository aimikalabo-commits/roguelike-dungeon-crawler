from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine import Engine

XP_PER_LEVEL = 150   # multiplied by current_level


class Level:
    def __init__(
        self,
        xp_given: int = 0,
        current_level: int = 1,
        current_xp: int = 0,
    ) -> None:
        self.xp_given      = xp_given
        self.current_level = current_level
        self.current_xp    = current_xp
        self.entity        = None  # back-reference set by Entity

    @property
    def xp_to_next_level(self) -> int:
        return self.current_level * XP_PER_LEVEL

    @property
    def requires_level_up(self) -> bool:
        return self.current_xp >= self.xp_to_next_level

    # ------------------------------------------------------------------
    # Called when XP is earned
    # ------------------------------------------------------------------

    def add_xp(self, xp: int, engine: Engine) -> None:
        from game import color
        if xp == 0:
            return
        self.current_xp += xp
        engine.message_log.add(f"You gain {xp} experience.", fg=color.YELLOW)
        if self.requires_level_up:
            engine.message_log.add(
                f"Level up! You reached level {self.current_level + 1}!",
                fg=color.YELLOW,
            )
            from game.input_handlers import LevelUpEventHandler
            engine.handler = LevelUpEventHandler()

    # ------------------------------------------------------------------
    # Called when a stat boost is chosen
    # ------------------------------------------------------------------

    def _advance(self) -> None:
        self.current_xp -= self.xp_to_next_level
        self.current_level += 1

    def increase_max_hp(self, engine: Engine) -> None:
        from game import color
        self.entity.fighter.max_hp += 20
        self.entity.fighter.hp = min(
            self.entity.fighter.hp + 20, self.entity.fighter.max_hp
        )
        engine.message_log.add("Your health improves!", fg=color.GREEN)
        self._advance()

    def increase_attack(self, engine: Engine) -> None:
        from game import color
        self.entity.fighter.attack += 1
        engine.message_log.add("You feel stronger!", fg=color.RED)
        self._advance()

    def increase_defense(self, engine: Engine) -> None:
        from game import color
        self.entity.fighter.defense += 1
        engine.message_log.add("Your skin hardens!", fg=color.CYAN)
        self._advance()
