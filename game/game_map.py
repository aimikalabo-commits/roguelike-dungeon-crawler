from __future__ import annotations
from typing import Iterable, Optional, TYPE_CHECKING

import numpy as np
import tcod

from game import tile_types

if TYPE_CHECKING:
    from tcod.console import Console
    from game.entity import Entity


class GameMap:
    def __init__(self, width: int, height: int, entities: Iterable[Entity] = ()) -> None:
        self.width = width
        self.height = height
        self.entities: set[Entity] = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, dtype=tile_types.tile_dt)
        self.visible  = np.full((width, height), fill_value=False, dtype=bool)
        self.explored = np.full((width, height), fill_value=False, dtype=bool)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_blocking_entity_at(self, x: int, y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == x and entity.y == y:
                return entity
        return None

    def render(self, console: Console) -> None:
        """Blit tile graphics to the console respecting FOV / explored state."""
        console.tiles_rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )
