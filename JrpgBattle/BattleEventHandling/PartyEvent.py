from __future__ import annotations
from enum import Enum, auto
from typing import Set, TYPE_CHECKING

from JrpgBattle.BattleEventHandling.EventManagement import BattleEvent

if TYPE_CHECKING:
    from JrpgBattle.Party import Party


class PartyEventType(Enum):
    TURN_STARTED = auto()
    START_INTERVAL = auto()
    FINISH_INTERVAL = auto()
    TURN_FINISHED = auto()


class PartyEvent(BattleEvent):
    def __init__(self,
                 party: Party,
                 event_type: PartyEventType,
                 cause: BattleEvent = None):
        super().__init__(cause=cause)
        self.party = party
        self.event_type = event_type

    def __str__(self):
        if self.event_type == PartyEventType.TURN_STARTED:
            return f'==== Team {self.party.name}: TURN START ====\n' \
                   f'Team {self.party.name} enters attack phase'
        elif self.event_type == PartyEventType.START_INTERVAL:
            return f'Team {self.party.name} exits attack phase'
        elif self.event_type == PartyEventType.FINISH_INTERVAL:
            return f'Team {self.party.name} enters planning phase'
        elif self.event_type == PartyEventType.TURN_FINISHED:
            return f'Team {self.party.name} exits planning phase\n' \
                   f'==== Team {self.party.name}: TURN FINISHED ===='
        else:
            return "invalid event_type"
