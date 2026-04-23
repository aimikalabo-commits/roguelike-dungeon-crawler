"""
Template entities for all monsters and items.
Never place templates directly — always use spawn() to get a deep copy.
"""
from __future__ import annotations

import copy
import random
from typing import List, Tuple

from game.components.ai import BasicMonster
from game.components.fighter import Fighter
from game.components.item import Item
from game.components.level import Level
from game.entity import Entity
from game import color, item_functions

# ---------------------------------------------------------------------------
# Spawn helper
# ---------------------------------------------------------------------------

def spawn(template: Entity, x: int, y: int) -> Entity:
    clone = copy.deepcopy(template)
    clone.x = x
    clone.y = y
    return clone

# ---------------------------------------------------------------------------
# Monster templates
# ---------------------------------------------------------------------------

rat = Entity(
    0, 0, "r", (130, 110, 90), "rat",
    blocks_movement=True,
    fighter=Fighter(hp=2,  attack=2, defense=0),
    ai=BasicMonster(),
    level=Level(xp_given=10),
)

goblin = Entity(
    0, 0, "g", (80, 160, 80), "goblin",
    blocks_movement=True,
    fighter=Fighter(hp=6,  attack=3, defense=0),
    ai=BasicMonster(),
    level=Level(xp_given=25),
)

orc = Entity(
    0, 0, "o", (63, 127, 63), "orc",
    blocks_movement=True,
    fighter=Fighter(hp=10, attack=4, defense=0),
    ai=BasicMonster(),
    level=Level(xp_given=35),
)

troll = Entity(
    0, 0, "T", (0, 127, 0), "troll",
    blocks_movement=True,
    fighter=Fighter(hp=16, attack=5, defense=1),
    ai=BasicMonster(),
    level=Level(xp_given=100),
)

ogre = Entity(
    0, 0, "O", (0, 80, 0), "ogre",
    blocks_movement=True,
    fighter=Fighter(hp=25, attack=6, defense=2),
    ai=BasicMonster(),
    level=Level(xp_given=200),
)

# ---------------------------------------------------------------------------
# Item templates
# ---------------------------------------------------------------------------

health_potion = Entity(
    0, 0, "!", (127, 0, 255), "health potion",
    blocks_movement=False,
    item=Item(use_fn=item_functions.heal(amount=8)),
)

# ---------------------------------------------------------------------------
# Spawn tables  (min_floor, weight, template)
# ---------------------------------------------------------------------------

_MONSTER_TABLE: List[Tuple[int, int, Entity]] = [
    (1,  80, rat),
    (1,  60, goblin),
    (2,  40, orc),
    (4,  20, troll),
    (6,  10, ogre),
]

_ITEM_TABLE: List[Tuple[int, int, Entity]] = [
    (1, 100, health_potion),
]


def max_monsters_by_floor(floor: int) -> int:
    return min(2 + (floor - 1) // 2, 5)


def max_items_by_floor(floor: int) -> int:
    return min(1 + floor // 4, 3)


def _weighted_choice(table: List[Tuple[int, int, Entity]], floor: int) -> Entity:
    eligible = [(w, tmpl) for min_f, w, tmpl in table if floor >= min_f]
    weights   = [w for w, _ in eligible]
    templates = [t for _, t in eligible]
    return random.choices(templates, weights=weights, k=1)[0]


def get_random_monster(floor: int, x: int, y: int) -> Entity:
    return spawn(_weighted_choice(_MONSTER_TABLE, floor), x, y)


def get_random_item(floor: int, x: int, y: int) -> Entity:
    return spawn(_weighted_choice(_ITEM_TABLE, floor), x, y)
