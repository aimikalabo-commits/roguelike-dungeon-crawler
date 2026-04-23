from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine import Engine


class BasicMonster:
    """Chases and attacks the player when inside the player's FOV."""

    def __init__(self) -> None:
        self.entity = None  # back-reference set by Entity

    def perform(self, engine: Engine) -> None:
        monster = self.entity
        if not engine.game_map.visible[monster.x, monster.y]:
            return  # can't see player — stay put

        dx = engine.player.x - monster.x
        dy = engine.player.y - monster.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance

        if distance <= 1:
            if engine.player.fighter.is_alive:
                monster.fighter.do_attack(engine.player.fighter, engine)
        else:
            # Single-step toward player
            step_x = 0 if dx == 0 else dx // abs(dx)
            step_y = 0 if dy == 0 else dy // abs(dy)
            dest_x = monster.x + step_x
            dest_y = monster.y + step_y
            if (engine.game_map.tiles["walkable"][dest_x, dest_y]
                    and not engine.game_map.get_blocking_entity_at(dest_x, dest_y)):
                monster.move(step_x, step_y)
