"""Use-functions for items. Each returns a closure that matches Item.use_fn signature."""
from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine import Engine


def heal(amount: int) -> Callable[[Engine], bool]:
    def use_fn(engine: Engine) -> bool:
        from game import color
        player = engine.player
        if player.fighter.hp >= player.fighter.max_hp:
            engine.message_log.add(
                "You are already at full health.", fg=color.YELLOW
            )
            return False
        healed = min(amount, player.fighter.max_hp - player.fighter.hp)
        player.fighter.hp += healed
        engine.message_log.add(
            f"You drink the potion, healing {healed} HP!", fg=color.GREEN
        )
        return True
    return use_fn
