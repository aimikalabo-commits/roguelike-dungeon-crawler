from __future__ import annotations

import random
from typing import Iterator, List, Tuple

import tcod

from game import tile_types
from game.components.ai import BasicMonster
from game.components.fighter import Fighter
from game.entity import Entity
from game.game_map import GameMap

MAX_MONSTERS_PER_ROOM = 2


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    @property
    def inner(self) -> Tuple[slice, slice]:
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    x1, y1 = start
    x2, y2 = end
    corner = (x2, y1) if random.random() < 0.5 else (x1, y2)
    for x, y in tcod.los.bresenham((x1, y1), corner).tolist():
        yield x, y
    for x, y in tcod.los.bresenham(corner, (x2, y2)).tolist():
        yield x, y


def place_entities(room: RectangularRoom, dungeon: GameMap) -> None:
    num = random.randint(0, MAX_MONSTERS_PER_ROOM)
    for _ in range(num):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)
        if any(e.x == x and e.y == y for e in dungeon.entities):
            continue
        if random.random() < 0.8:
            monster = Entity(
                x, y, "o", (63, 127, 63), name="orc",
                blocks_movement=True,
                fighter=Fighter(hp=10, attack=3, defense=0),
                ai=BasicMonster(),
            )
        else:
            monster = Entity(
                x, y, "T", (0, 127, 0), name="troll",
                blocks_movement=True,
                fighter=Fighter(hp=16, attack=4, defense=1),
                ai=BasicMonster(),
            )
        dungeon.entities.add(monster)


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    player: Entity,
) -> GameMap:
    dungeon = GameMap(map_width, map_height)
    rooms: List[RectangularRoom] = []

    for _ in range(max_rooms):
        w = random.randint(room_min_size, room_max_size)
        h = random.randint(room_min_size, room_max_size)
        x = random.randint(0, map_width  - w - 1)
        y = random.randint(0, map_height - h - 1)

        new_room = RectangularRoom(x, y, w, h)
        if any(new_room.intersects(r) for r in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        if not rooms:
            player.x, player.y = new_room.center
        else:
            for cx, cy in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[cx, cy] = tile_types.floor
            place_entities(new_room, dungeon)

        rooms.append(new_room)

    # Stairs in the centre of the last room
    sx, sy = rooms[-1].center
    dungeon.tiles[sx, sy] = tile_types.stairs_down
    dungeon.downstairs_location = (sx, sy)

    return dungeon
