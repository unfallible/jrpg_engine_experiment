from typing import Set, Dict, MutableSet

from JrpgBattle.Attack import AttackQueue
from JrpgBattle.Character import CharacterStatus
from JrpgBattle.IdentifierSet import Identifier, IdentifierSet


class PartyIdentifier(Identifier):
    DOMAIN: str = "party"

    def __init__(self, name: str):
        super(PartyIdentifier, self).__init__(name)
        self.name = name

    def get_domain(self) -> object:
        return PartyIdentifier.DOMAIN


class Party(PartyIdentifier):
    def __init__(self,
                 name: str,
                 characters: MutableSet[CharacterStatus] = set(),  # the characters in the user_party
                 attack_queue: AttackQueue = AttackQueue(),  # the queue of attacks which the user_party will execute in the next turn
                 current_mp: int = 0):  # the current mana points. MP is a shared resource
        PartyIdentifier.__init__(self, name)
        self.characters: IdentifierSet[CharacterStatus] = IdentifierSet(characters)
        self.attack_queue = attack_queue
        self._current_mp = current_mp

    def get_name(self) -> str:
        return self.name

    @property
    def __iter__(self):
        return self.characters.__iter__()

    def __contains__(self, item):
        return item in self.characters

    def is_wiped_out(self) -> bool:
        for member in self.characters.values():
            if not member.is_dead():
                return False
        return True

    # TODO: Translating CharacterIdentifiers to CharacterStatuses should probably be done elsewhere
    # def get_status(self, character_id: CharacterIdentifier) -> CharacterStatus:
    #     return self.characters[character_id]

    def get_mp(self) -> int:
        return self._current_mp

    def spend_mp(self, cost: int) -> bool:
        if self._current_mp >= cost:
            self._current_mp -= cost
            return True
        else:
            return False
