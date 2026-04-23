from __future__ import annotations

from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.components.ai import BasicMonster
    from game.components.fighter import Fighter
    from game.components.item import Item
    from game.components.level import Level


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
        level: Optional[Level] = None,
        item: Optional[Item] = None,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.fighter  = fighter
        self.ai       = ai
        self.level    = level
        self.item     = item
        self.inventory: List[Entity] = []

        for component in (self.fighter, self.ai, self.level, self.item):
            if component is not None:
                component.entity = self  # type: ignore[attr-defined]

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
