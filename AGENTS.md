# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single standalone product: a **tcod-based roguelike dungeon crawler** (Python). There is no backend, database, or web service — the "service" is the GUI game process itself. Entry point is `main.py`; game logic lives in `game/`.

### Running the game
- Run it with the project venv: `.venv/bin/python main.py` (from repo root). See `README.md` for controls.
- It is a **GUI/SDL desktop app**, not a headless CLI. It opens a window titled `Roguelike` and blocks in an interactive event loop, so launch it in a background/tmux session (or with a timeout) rather than a blocking foreground shell. This VM has a display available at `DISPLAY=:1`.
- Interact/verify via the Desktop (computer use), e.g. arrow keys or vi keys (`h`/`j`/`k`/`l`) to move the `@` player.

### Non-obvious gotchas
- **Required asset, not committed:** `main.py` calls `sys.exit(...)` at startup if `dejavu10x10_gs_tc.png` is missing. It is git-ignored, so it must be downloaded (the update script fetches it). Download URL is in `README.md`.
- **tcod version matters:** the code uses the pre-SDL3 tcod API (e.g. lowercase `tcod.event.KeySym.h`). tcod 19+ (SDL3 rewrite) removed these, so `requirements.txt` pins `tcod>=16.2,<19`. Do not "upgrade" tcod past 18.x without also updating `game/input_handlers.py`.
- A harmless `FutureWarning` about `console.tiles_rgb` being renamed to `rgb` prints on render; it does not affect functionality.

### Testing / lint / build
- There is **no** test suite, linter, or build step in this repo (no pytest/tox/CI/Makefile). "Building" = running the game. Validate changes by launching the game and playing it via the Desktop.
