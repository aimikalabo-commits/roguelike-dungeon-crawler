from __future__ import annotations

from typing import Tuple

import tcod.console

from game import color


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
    console.draw_rect(0,      y, total_width, 1, ord(" "), bg=empty_color)
    if filled > 0:
        console.draw_rect(0,  y, filled,      1, ord(" "), bg=full_color)
    console.print(1, y, f"{label}: {current}/{maximum}", fg=color.WHITE)
