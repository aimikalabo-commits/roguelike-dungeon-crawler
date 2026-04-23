#!/usr/bin/env python3
"""Entry point for the roguelike dungeon crawler."""

import sys
from pathlib import Path

import tcod

from game import color, procgen
from game.components.fighter import Fighter
from game.components.level import Level
from game.engine import Engine
from game.entity import Entity

# --- Screen layout ----------------------------------------------------------
SCREEN_WIDTH  = 80
SCREEN_HEIGHT = 50   # 43 map + 1 status bar + 6 message log
MAP_WIDTH     = 80
MAP_HEIGHT    = 43   # must match engine.MAP_HEIGHT

# --- Dungeon parameters -----------------------------------------------------
ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 12
MAX_ROOMS     = 30

# --- Tileset ----------------------------------------------------------------
TILESET_FILE = Path(__file__).parent / "dejavu10x10_gs_tc.png"


def main() -> None:
    if not TILESET_FILE.exists():
        sys.exit(
            f"Tileset not found: {TILESET_FILE}\n"
            "Download it with:\n"
            "  curl -L -o dejavu10x10_gs_tc.png "
            "https://raw.githubusercontent.com/libtcod/libtcod/main/data/fonts/dejavu10x10_gs_tc.png"
        )

    tileset = tcod.tileset.load_tilesheet(
        str(TILESET_FILE), 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = Entity(
        x=0, y=0,
        char="@", color=color.WHITE,
        name="Player",
        blocks_movement=True,
        fighter=Fighter(hp=30, attack=5, defense=2),
        level=Level(current_level=1),
    )

    game_map = procgen.generate_dungeon(
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE,
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        player=player,
        floor_number=1,
    )

    engine = Engine(player=player, game_map=game_map)

    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title="Roguelike",
        vsync=True,
    ) as context:
        console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        while True:
            console.clear()
            engine.render(console)
            context.present(console)
            engine.handle_events()


if __name__ == "__main__":
    main()
