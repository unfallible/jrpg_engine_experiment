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
    DEFENSE_WHIFFED = auto()
    VULNERABILITY_RESET = auto()
    VULNERABILITY_RAISED = auto()
    CHARACTER_DIED = auto()


class CharacterUpdateEvent(BattleEvent):
    def __init__(self,
                 character: CharacterStatus,
                 event_type: UpdateType,
                 hp_change: int = 0,
                 sp_change: int = 0,
                 vulnerability_change: int = 0,
                 character_staggers: bool = False,
                 character_died: bool = False,
                 cause: BattleEvent = None):
        super().__init__(cause=cause)
        self.character = character
        self.event_type = event_type
        self.hp_change = hp_change
        self.sp_change = sp_change
        self.vulnerability_change = vulnerability_change
        self.character_staggers = character_staggers
        self.character_died = character_died

    def __str__(self):
        if self.event_type == UpdateType.SP_GAINED:
            return f'{self.character.character_name} gains {self.sp_change} SP.'
        elif self.event_type == UpdateType.SP_SPENT:
            return f'{self.character.character_name} spends {-1 * self.sp_change} SP.'
        elif self.event_type == UpdateType.DAMAGE_INCURRED:
            return f'{self.character.character_name} takes {self.hp_change} damage.'
        elif self.event_type == UpdateType.DEFENSE_WHIFFED:
            defense_target = 'themselves' if self.character.is_defending == self.character \
                else self.character.is_defending.character_name
            return f'{self.character.character_name} defended {defense_target}, but nobody attacked. ' \
                   f'{self.character.character_name} staggers.'
        elif self.event_type == UpdateType.VULNERABILITY_RESET:
            return f'{self.character.character_name} was properly defended. ' \
                   f'{self.character.character_name}\'s guard is reset.'
        elif self.event_type == UpdateType.VULNERABILITY_RAISED:
            return f'{self.character.character_name} was defended, but nobody attacked. ' \
                   f'{self.character.character_name}\'s guard drops by {self.vulnerability_change}.'
        elif self.event_type == UpdateType.CHARACTER_DIED:
            return f'{self.character.character_name} died.'
        else:
            return "invalid update event_type"
