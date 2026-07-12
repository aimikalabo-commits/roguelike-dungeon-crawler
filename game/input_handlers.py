from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import tcod.event

if TYPE_CHECKING:
    from game.engine import Engine


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

class Action:
    def perform(self, engine: Engine) -> bool:
        """Perform the action. Returns True if it consumed the player's turn."""
        raise NotImplementedError


class EscapeAction(Action):
    def perform(self, engine: Engine) -> bool:
        raise SystemExit


class WaitAction(Action):
    def perform(self, engine: Engine) -> bool:
        return True  # burns the player's turn


class MovementAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine) -> bool:
        from game import color
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy
        if (
            not engine.game_map.in_bounds(dest_x, dest_y)
            or not engine.game_map.tiles["walkable"][dest_x, dest_y]
            or engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        ):
            engine.message_log.add("That way is blocked.", fg=color.WHITE)
            return False
        engine.player.move(self.dx, self.dy)
        engine.update_fov()
        return True


class MeleeAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine) -> bool:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy
        target = engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        if not target or not target.fighter:
            return False
        engine.player.fighter.do_attack(target.fighter, engine)
        return True


class BumpAction(Action):
    """Resolves to MeleeAction or MovementAction based on what's at the destination."""

    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine) -> bool:
        dest_x = engine.player.x + self.dx
        dest_y = engine.player.y + self.dy
        target = engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        if target and target.fighter:
            return MeleeAction(self.dx, self.dy).perform(engine)
        return MovementAction(self.dx, self.dy).perform(engine)


class PickupAction(Action):
    def perform(self, engine: Engine) -> bool:
        from game import color
        player = engine.player
        item_here = next(
            (i for i in engine.game_map.items if i.x == player.x and i.y == player.y),
            None,
        )
        if not item_here:
            engine.message_log.add("Nothing to pick up here.", fg=color.WHITE)
            return False
        if len(player.inventory) >= 5:
            engine.message_log.add("Inventory full! (max 5 items)", fg=color.YELLOW)
            return False
        engine.game_map.items.discard(item_here)
        player.inventory.append(item_here)
        engine.message_log.add(
            f"You pick up the {item_here.name}.", fg=color.WHITE
        )
        return True


class UseItemAction(Action):
    def perform(self, engine: Engine) -> bool:
        from game import color
        player = engine.player
        for item in player.inventory:
            if item.item:
                success = item.item.use(engine)
                if success:
                    player.inventory.remove(item)
                return success
        engine.message_log.add("No usable items in inventory.", fg=color.WHITE)
        return False


class TakeStairsAction(Action):
    def perform(self, engine: Engine) -> bool:
        from game import color
        if (engine.player.x, engine.player.y) == engine.game_map.downstairs_location:
            engine.descend()
            return True
        engine.message_log.add("There are no stairs here.", fg=color.WHITE)
        return False


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
    tcod.event.KeySym.H: (-1,  0),
    tcod.event.KeySym.J: ( 0,  1),
    tcod.event.KeySym.K: ( 0, -1),
    tcod.event.KeySym.L: ( 1,  0),
    tcod.event.KeySym.Y: (-1, -1),
    tcod.event.KeySym.U: ( 1, -1),
    tcod.event.KeySym.B: (-1,  1),
    tcod.event.KeySym.N: ( 1,  1),
}

WAIT_KEYS = {tcod.event.KeySym.KP_5, tcod.event.KeySym.Z}

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
            elif sym == tcod.event.KeySym.G:
                action = PickupAction()
            elif sym == tcod.event.KeySym.Q:
                # q = quaff/use item ('u' is taken by vi diagonal movement)
                action = UseItemAction()
            elif sym == tcod.event.KeySym.PERIOD and shift:
                action = TakeStairsAction()

        if action is not None:
            turn_consumed = action.perform(engine)
            if turn_consumed:
                engine.handle_enemy_turns()
                engine.check_player_death()


class LevelUpEventHandler(EventHandler):
    def handle_event(self, engine: Engine, event: tcod.event.Event) -> None:
        if isinstance(event, tcod.event.Quit):
            raise SystemExit

        if isinstance(event, tcod.event.KeyDown):
            player = engine.player
            chosen = None

            if event.sym == tcod.event.KeySym.A:
                chosen = player.level.increase_max_hp
            elif event.sym == tcod.event.KeySym.B:
                chosen = player.level.increase_attack
            elif event.sym == tcod.event.KeySym.C:
                chosen = player.level.increase_defense

            if chosen is not None:
                chosen(engine)
                # Banked XP may cover several levels at once; keep the menu
                # open until every pending level-up has been spent.
                if not player.level.requires_level_up:
                    engine.handler = MainGameEventHandler()


class GameOverEventHandler(EventHandler):
    def handle_event(self, engine: Engine, event: tcod.event.Event) -> None:
        if isinstance(event, tcod.event.Quit):
            raise SystemExit
        if isinstance(event, tcod.event.KeyDown):
            if event.sym == tcod.event.KeySym.ESCAPE:
                raise SystemExit
