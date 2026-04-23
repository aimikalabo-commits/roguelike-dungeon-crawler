from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
import tcod.event

from game import color
from game.message_log import MessageLog
from game.render_functions import render_bar, render_level_up_menu

if TYPE_CHECKING:
    from tcod.console import Console
    from game.entity import Entity
    from game.game_map import GameMap
    from game.input_handlers import EventHandler

# UI layout constants (rows) — must stay in sync with SCREEN_HEIGHT in main.py
MAP_HEIGHT = 43
BAR_WIDTH  = 20
BAR_Y      = MAP_HEIGHT       # row 43: status line
LOG_Y      = MAP_HEIGHT + 1   # row 44: top of message log
LOG_HEIGHT = 6                # rows 44-49


class Engine:
    def __init__(
        self,
        player: Entity,
        game_map: GameMap,
        floor_number: int = 1,
    ) -> None:
        from game.input_handlers import MainGameEventHandler
        self.player       = player
        self.game_map     = game_map
        self.floor_number = floor_number
        self.message_log  = MessageLog()
        self.handler: EventHandler = MainGameEventHandler()
        self.update_fov()
        self.message_log.add("Welcome, adventurer! Good luck.", fg=color.CYAN)

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            self.handler.handle_event(self, event)

    def handle_enemy_turns(self) -> None:
        for entity in list(self.game_map.entities):
            if entity.ai and entity.fighter and entity.fighter.is_alive:
                entity.ai.perform(self)

    # ------------------------------------------------------------------
    # State changes
    # ------------------------------------------------------------------

    def update_fov(self) -> None:
        self.game_map.visible[:] = tcod.map.compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        self.game_map.explored |= self.game_map.visible

    def check_player_death(self) -> None:
        if not self.player.fighter.is_alive:
            from game.input_handlers import GameOverEventHandler
            self.message_log.add("You died! Press Esc to quit.", fg=color.RED)
            self.player.char  = "%"
            self.player.color = color.RED
            self.handler = GameOverEventHandler()

    def descend(self) -> None:
        from game import procgen
        self.floor_number += 1
        self.game_map = procgen.generate_dungeon(
            max_rooms=30,
            room_min_size=5,
            room_max_size=12,
            map_width=80,
            map_height=MAP_HEIGHT,
            player=self.player,
            floor_number=self.floor_number,
        )
        self.message_log.add(
            f"You descend deeper… (floor {self.floor_number})", fg=color.CYAN
        )
        self.update_fov()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, console: Console) -> None:
        # Map tiles
        self.game_map.render(console)

        # Items: show when explored (they don't move)
        for item in self.game_map.items:
            if self.game_map.explored[item.x, item.y]:
                console.print(item.x, item.y, item.char, fg=item.color)

        # Monsters: only when in FOV
        for entity in self.game_map.entities:
            if self.game_map.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)

        # Player always on top
        console.print(self.player.x, self.player.y, self.player.char, fg=self.player.color)

        # --- Status bar (row 43) ---
        p = self.player
        render_bar(
            console,
            current=p.fighter.hp,
            maximum=p.fighter.max_hp,
            total_width=BAR_WIDTH,
            y=BAR_Y,
            label="HP",
            full_color=color.HP_BAR_FULL,
            empty_color=color.HP_BAR_EMPTY,
        )
        lv  = p.level.current_level
        xp  = p.level.current_xp
        nxt = p.level.xp_to_next_level
        potions = sum(1 for i in p.inventory if i.item)
        console.print(
            BAR_WIDTH + 1, BAR_Y,
            f"Floor:{self.floor_number}  Lv:{lv}  XP:{xp}/{nxt}  !:{potions}",
            fg=color.YELLOW,
        )

        # --- Message log (rows 44-49) ---
        self.message_log.render(console, x=0, y=LOG_Y, width=80, height=LOG_HEIGHT)

        # --- Level-up overlay (drawn last so it's on top) ---
        from game.input_handlers import LevelUpEventHandler
        if isinstance(self.handler, LevelUpEventHandler):
            render_level_up_menu(console, self.player)
