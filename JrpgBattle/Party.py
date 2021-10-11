from typing import Set, Dict, MutableSet

from JrpgBattle.Attack import AttackQueue
from JrpgBattle.BattleEventHandling.EventManagement import EventSubject
from JrpgBattle.BattleEventHandling.PartyEvent import PartyEventType, PartyEvent
from JrpgBattle.Character import CharacterStatus
from JrpgBattle.IdentifierSet import Identifier, IdentifierSet


class PartyIdentifier(Identifier):
    DOMAIN: str = "party"

    def __init__(self, name: str):
        super(PartyIdentifier, self).__init__(name)
        self.name = name

    def get_domain(self) -> object:
        return PartyIdentifier.DOMAIN


class Party(PartyIdentifier, EventSubject[PartyEvent]):
    def __init__(self,
                 name: str,
                 characters: MutableSet[CharacterStatus] = set(),  # the characters in the user_party
                 attack_queue: AttackQueue = AttackQueue(),  # the queue of attacks which the user_party will execute in the next turn
                 current_mp: int = 0):  # the current mana points. MP is a shared resource
        PartyIdentifier.__init__(self, name)
        EventSubject.__init__(self)
        self.characters: IdentifierSet[CharacterStatus] = IdentifierSet(characters)
        self.attack_queue = attack_queue
        self._current_mp = current_mp

    def get_name(self) -> str:
        return self.name

    def __iter__(self):
        for c in self.characters:
            yield c

    def __contains__(self, item):
        return item in self.characters

    def is_wiped_out(self) -> bool:
        for member in self.characters:
            if not member.is_dead():
                return False
        return True

    def start_turn(self):
        party_event = PartyEvent(self, PartyEventType.TURN_STARTED)
        self.notify_observers(party_event)
        for member in self.characters:
            member.start_turn()

    def end_turn(self):
        for member in self.characters:
            member.end_turn()
        party_event = PartyEvent(self, PartyEventType.TURN_FINISHED)
        self.notify_observers(party_event)

    def turn_interval(self):
        party_event = PartyEvent(self, PartyEventType.START_INTERVAL)
        self.notify_observers(party_event)
        for member in self.characters:
            member.turn_interval()
        party_event = PartyEvent(self, PartyEventType.FINISH_INTERVAL)
        self.notify_observers(party_event)

    def get_mp(self) -> int:
        return self._current_mp

    def spend_mp(self, cost: int) -> bool:
        if self._current_mp >= cost:
            self._current_mp -= cost
            return True
        else:
            return False
