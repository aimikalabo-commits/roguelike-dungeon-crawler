from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
import tcod.event

from game import input_handlers

if TYPE_CHECKING:
    from tcod.console import Console
    from game.entity import Entity
    from game.game_map import GameMap


class Engine:
    def __init__(self, player: Entity, game_map: GameMap) -> None:
        self.player   = player
        self.game_map = game_map
        self.update_fov()

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = input_handlers.handle_event(event)
            if action is not None:
                action.perform(self)

    def update_fov(self) -> None:
        self.game_map.visible[:] = tcod.map.compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)
        # Draw monsters only when visible
        for entity in self.game_map.entities:
            if self.game_map.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)
        # Player always on top
        console.print(self.player.x, self.player.y, self.player.char, fg=self.player.color)
