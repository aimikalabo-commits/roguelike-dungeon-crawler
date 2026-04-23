from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import tcod.console

from game import color

if TYPE_CHECKING:
    from game.entity import Entity


def render_bar(
    console: tcod.console.Console,
    current: int,
    maximum: int,
    total_width: int,
    y: int,
    label: str,
    full_color: Tuple[int, int, int],
    empty_color: Tuple[int, int, int],
) -> None:
    filled = int(current / maximum * total_width)
    console.draw_rect(0,     y, total_width, 1, ord(" "), bg=empty_color)
    if filled > 0:
        console.draw_rect(0, y, filled,      1, ord(" "), bg=full_color)
    console.print(1, y, f"{label}: {current}/{maximum}", fg=color.WHITE)


def render_level_up_menu(
    console: tcod.console.Console,
    player: Entity,
) -> None:
    x, y, w, h = 10, 4, 44, 11
    console.draw_frame(
        x, y, w, h,
        title=" *** Level Up! *** ",
        clear=True,
        fg=color.YELLOW,
        bg=color.BLACK,
    )
    lv = player.level.current_level + 1
    console.print(x + 1, y + 1, f"You have reached level {lv}!", fg=color.YELLOW)
    console.print(x + 1, y + 2, "Choose a stat to improve:", fg=color.WHITE)

    f = player.fighter
    console.print(x + 1, y + 4, f"[a] Constitution  +20 max HP  (now {f.max_hp} HP)",  fg=color.GREEN)
    console.print(x + 1, y + 5, f"[b] Strength      +1 attack   (now {f.attack} Atk)", fg=color.RED)
    console.print(x + 1, y + 6, f"[c] Agility       +1 defense  (now {f.defense} Def)",fg=color.CYAN)
