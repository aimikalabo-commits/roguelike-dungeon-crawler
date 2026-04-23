import numpy as np

# dtype for a single rendered tile: Unicode codepoint + fg/bg colours
graphic_dt = np.dtype([
    ("ch", np.int32),
    ("fg", "3B"),
    ("bg", "3B"),
])

# dtype for a map tile: passability flags + two render states
tile_dt = np.dtype([
    ("walkable",    bool),
    ("transparent", bool),
    ("dark",  graphic_dt),  # rendered when explored but out of FOV
    ("light", graphic_dt),  # rendered when inside FOV
])


def new_tile(*, walkable: int, transparent: int, dark: tuple, light: tuple) -> np.ndarray:
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# Shown for unexplored cells
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."),  (50,  50,  80),  (0, 0, 30)),
    light=(ord("."), (170, 170, 170), (0, 0, 50)),
)

wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"),  (60,  60,  100), (0, 0, 30)),
    light=(ord("#"), (200, 180, 50),  (60, 50, 10)),
)
