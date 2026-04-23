from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import tcod.event

if TYPE_CHECKING:
    from game.engine import Engine


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

class Action:
    def perform(self, engine: Engine) -> None:
        raise NotImplementedError


class EscapeAction(Action):
    def perform(self, engine: Engine) -> None:
        raise SystemExit


class MovementAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine) -> None:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy

        if not engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        if engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            return  # bump blocks movement; combat wired in step 6

        engine.player.move(self.dx, self.dy)
        engine.update_fov()


# ---------------------------------------------------------------------------
# Key → action mapping
# ---------------------------------------------------------------------------

MOVE_KEYS: dict[tcod.event.KeySym, tuple[int, int]] = {
    # Arrow keys
    tcod.event.KeySym.UP:    (0, -1),
    tcod.event.KeySym.DOWN:  (0,  1),
    tcod.event.KeySym.LEFT:  (-1, 0),
    tcod.event.KeySym.RIGHT: (1,  0),
    # Numpad (8-directional)
    tcod.event.KeySym.KP_1: (-1,  1),
    tcod.event.KeySym.KP_2: ( 0,  1),
    tcod.event.KeySym.KP_3: ( 1,  1),
    tcod.event.KeySym.KP_4: (-1,  0),
    tcod.event.KeySym.KP_6: ( 1,  0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: ( 0, -1),
    tcod.event.KeySym.KP_9: ( 1, -1),
    # Vi keys
    tcod.event.KeySym.h: (-1,  0),
    tcod.event.KeySym.j: ( 0,  1),
    tcod.event.KeySym.k: ( 0, -1),
    tcod.event.KeySym.l: ( 1,  0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: ( 1, -1),
    tcod.event.KeySym.b: (-1,  1),
    tcod.event.KeySym.n: ( 1,  1),
}


def handle_event(event: tcod.event.Event) -> Optional[Action]:
    if isinstance(event, tcod.event.Quit):
        return EscapeAction()

    if isinstance(event, tcod.event.KeyDown):
        if event.sym == tcod.event.KeySym.ESCAPE:
            return EscapeAction()
        if event.sym in MOVE_KEYS:
            dx, dy = MOVE_KEYS[event.sym]
            return MovementAction(dx, dy)

    return None
