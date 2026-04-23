from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.components.ai import BasicMonster
    from game.components.fighter import Fighter


class Entity:
    """A generic object that exists on the map (player, monsters, items…)."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: Tuple[int, int, int],
        name: str = "",
        blocks_movement: bool = False,
        fighter: Optional[Fighter] = None,
        ai: Optional[BasicMonster] = None,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.fighter = fighter
        self.ai = ai
        if self.fighter:
            self.fighter.entity = self
        if self.ai:
            self.ai.entity = self

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
