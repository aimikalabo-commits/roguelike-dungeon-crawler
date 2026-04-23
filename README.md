# Roguelike Dungeon Crawler

A terminal-based roguelike built with Python + [tcod](https://python-tcod.readthedocs.io/).

## Features

- Procedurally generated dungeon (rooms connected by L-shaped corridors)
- Field-of-view with darkness / explored-map memory
- 8-directional movement via arrow keys, numpad, or vi keys

## Requirements

- Python 3.11+
- pip

## Installation

```bash
# 1. Clone / enter the project directory
cd roguelike

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the bitmap tileset (required, ~3 KB)
curl -L -o dejavu10x10_gs_tc.png \
  https://raw.githubusercontent.com/libtcod/libtcod/main/data/fonts/dejavu10x10_gs_tc.png
```

## Running

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys / Numpad | Move (8-directional) |
| `h j k l` | Move left / down / up / right (vi) |
| `y u b n` | Move diagonally (vi) |
| `Esc` | Quit |

## Project Structure

```
roguelike/
├── main.py               # Entry point
├── requirements.txt
├── dejavu10x10_gs_tc.png # Bitmap tileset (downloaded separately)
└── game/
    ├── color.py          # Colour constants
    ├── engine.py         # Main game loop, FOV updates
    ├── entity.py         # Base Entity class
    ├── game_map.py       # GameMap + numpy tile arrays
    ├── input_handlers.py # Key bindings → Action objects
    ├── procgen.py        # Procedural dungeon generation
    └── tile_types.py     # Tile dtype definitions (floor, wall, shroud)
```
