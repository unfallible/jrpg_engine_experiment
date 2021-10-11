from __future__ import annotations
from enum import Enum, auto
from typing import Set, TYPE_CHECKING

from JrpgBattle.BattleEventHandling.EventManagement import BattleEvent
if TYPE_CHECKING:
    from JrpgBattle.Character import CharacterStatus


class UpdateType(Enum):
    DAMAGE_INCURRED = auto()
    SP_GAINED = auto()
    SP_SPENT = auto()


class CharacterUpdateEvent(BattleEvent):
    def __init__(self,
                 character: CharacterStatus,
                 event_type: UpdateType,
                 hp_change: int = 0,
                 sp_change: int = 0,
                 cause: BattleEvent = None):
        super().__init__(cause=cause)
        self.character = character
        self.event_type = event_type
        self.hp_change = hp_change
        self.sp_change = sp_change

    def __str__(self):
        if self.event_type == UpdateType.SP_GAINED:
            return f'{self.character.character_name} gained {self.sp_change} SP.'
        elif self.event_type == UpdateType.SP_SPENT:
            return f'{self.character.character_name} spent {-1 * self.sp_change} SP.'
        elif self.event_type == UpdateType.DAMAGE_INCURRED:
            return f'{self.character.character_name} took {self.hp_change} damage.'
        else:
            return "invalid update event_type"
