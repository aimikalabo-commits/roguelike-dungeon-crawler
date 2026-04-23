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


class WaitAction(Action):
    def perform(self, engine: Engine) -> None:
        pass  # burns the player's turn


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
            return
        engine.player.move(self.dx, self.dy)
        engine.update_fov()


class MeleeAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine) -> None:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy
        target = engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        if not target or not target.fighter:
            return
        engine.player.fighter.do_attack(target.fighter, engine)


class BumpAction(Action):
    """Resolves to MeleeAction or MovementAction based on what's at the destination."""

    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine) -> None:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy
        target = engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        if target and target.fighter:
            MeleeAction(self.dx, self.dy).perform(engine)
        else:
            MovementAction(self.dx, self.dy).perform(engine)


class PickupAction(Action):
    def perform(self, engine: Engine) -> None:
        from game import color
        player = engine.player
        item_here = next(
            (i for i in engine.game_map.items if i.x == player.x and i.y == player.y),
            None,
        )
        if not item_here:
            engine.message_log.add("Nothing to pick up here.", fg=color.WHITE)
            return
        if len(player.inventory) >= 5:
            engine.message_log.add("Inventory full! (max 5 items)", fg=color.YELLOW)
            return
        engine.game_map.items.discard(item_here)
        player.inventory.append(item_here)
        engine.message_log.add(
            f"You pick up the {item_here.name}.", fg=color.WHITE
        )


class UseItemAction(Action):
    def perform(self, engine: Engine) -> None:
        from game import color
        player = engine.player
        for item in player.inventory:
            if item.item:
                success = item.item.use(engine)
                if success:
                    player.inventory.remove(item)
                return
        engine.message_log.add("No usable items in inventory.", fg=color.WHITE)


class TakeStairsAction(Action):
    def perform(self, engine: Engine) -> None:
        from game import color
        if (engine.player.x, engine.player.y) == engine.game_map.downstairs_location:
            engine.descend()
        else:
            engine.message_log.add("There are no stairs here.", fg=color.WHITE)


# ---------------------------------------------------------------------------
# Key maps
# ---------------------------------------------------------------------------

MOVE_KEYS: dict[tcod.event.KeySym, tuple[int, int]] = {
    # Arrow keys
    tcod.event.KeySym.UP:    (0, -1),
    tcod.event.KeySym.DOWN:  (0,  1),
    tcod.event.KeySym.LEFT:  (-1, 0),
    tcod.event.KeySym.RIGHT: (1,  0),
    # Numpad
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

WAIT_KEYS = {tcod.event.KeySym.KP_5, tcod.event.KeySym.z}

# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

class EventHandler:
    def handle_event(self, engine: Engine, event: tcod.event.Event) -> None:
        raise NotImplementedError


class MainGameEventHandler(EventHandler):
    def handle_event(self, engine: Engine, event: tcod.event.Event) -> None:
        if isinstance(event, tcod.event.Quit):
            raise SystemExit

        action: Optional[Action] = None

        if isinstance(event, tcod.event.KeyDown):
            sym   = event.sym
            shift = bool(event.mod & (tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT))

            if sym == tcod.event.KeySym.ESCAPE:
                action = EscapeAction()
            elif sym in MOVE_KEYS:
                dx, dy = MOVE_KEYS[sym]
                action = BumpAction(dx, dy)
            elif sym in WAIT_KEYS:
                action = WaitAction()
            elif sym == tcod.event.KeySym.g:
                action = PickupAction()
            elif sym == tcod.event.KeySym.u:
                action = UseItemAction()
            elif sym == tcod.event.KeySym.PERIOD and shift:
                action = TakeStairsAction()

        if action is not None:
            action.perform(engine)
            engine.handle_enemy_turns()
            engine.check_player_death()


class LevelUpEventHandler(EventHandler):
    def handle_event(self, engine: Engine, event: tcod.event.Event) -> None:
        if isinstance(event, tcod.event.Quit):
            raise SystemExit

        if isinstance(event, tcod.event.KeyDown):
            player = engine.player
            chosen = None

            if event.sym == tcod.event.KeySym.a:
                chosen = player.level.increase_max_hp
            elif event.sym == tcod.event.KeySym.b:
                chosen = player.level.increase_attack
            elif event.sym == tcod.event.KeySym.c:
                chosen = player.level.increase_defense

            if chosen is not None:
                chosen(engine)
                engine.handler = MainGameEventHandler()


class GameOverEventHandler(EventHandler):
    def handle_event(self, engine: Engine, event: tcod.event.Event) -> None:
        if isinstance(event, tcod.event.Quit):
            raise SystemExit
        if isinstance(event, tcod.event.KeyDown):
            if event.sym == tcod.event.KeySym.ESCAPE:
                raise SystemExit
