from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine import Engine


class Fighter:
    def __init__(self, hp: int, attack: int, defense: int) -> None:
        self.max_hp  = hp
        self.hp      = hp
        self.attack  = attack
        self.defense = defense
        self.entity  = None  # back-reference set by Entity

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def do_attack(self, target: Fighter, engine: Engine) -> None:
        from game import color
        damage   = max(0, self.attack - target.defense)
        attacker = self.entity.name.capitalize()
        victim   = target.entity.name.capitalize()

        if damage > 0:
            fg = color.PLAYER_ATK if self.entity is engine.player else color.ENEMY_ATK
            engine.message_log.add(f"{attacker} hits {victim} for {damage} HP.", fg=fg)
            target.hp = max(0, target.hp - damage)
            if not target.is_alive and target.entity is not engine.player:
                engine.message_log.add(f"{victim} dies!", fg=color.ORANGE)
                engine.game_map.entities.discard(target.entity)
                # Award XP to player
                if target.entity.level and engine.player.level:
                    engine.player.level.add_xp(target.entity.level.xp_given, engine)
        else:
            engine.message_log.add(
                f"{attacker} attacks {victim} but does no damage.", fg=color.WHITE
            )
