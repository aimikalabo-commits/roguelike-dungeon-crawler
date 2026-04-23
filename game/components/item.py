from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine import Engine


class Item:
    def __init__(self, use_fn: Callable[[Engine], bool]) -> None:
        self.use_fn = use_fn
        self.entity = None  # back-reference set by Entity

    def use(self, engine: Engine) -> bool:
        """Returns True if the item was consumed."""
        return self.use_fn(engine)
