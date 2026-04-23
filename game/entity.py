from __future__ import annotations
from typing import Tuple


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
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
