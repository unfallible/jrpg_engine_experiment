from typing import List, Set, Dict, Callable

from JrpgBattle.Attack import AttackQueue
from JrpgBattle.Character import CharacterStatus, CharacterIdentifier


class Party:
    def __init__(self,
                 characters: Set[CharacterStatus]=[],  # the characters in the user_party
                 attack_queue: AttackQueue=AttackQueue(),  # the queue of attacks which the user_party will execute in the next turn
                 current_mp: int=0):  # the current mana points. MP is a shared resource
        self._characters: Dict[CharacterIdentifier, CharacterStatus] = \
            {character: character for character in characters}
        self._attack_queue = attack_queue
        self._current_mp = current_mp

    @property
    def __iter__(self):
        return self._characters.__iter__()

    def __contains__(self, item):
        return item in self._characters

    def is_wiped_out(self) -> bool:
        for member in self._characters:
            if not member.is_dead():
                return False
        return True

    # TODO: Translating CharacterIdentifiers to CharacterStatuses should probably be done elsewhere
    def get_status(self, character_id: CharacterIdentifier) -> CharacterStatus:
        return self._characters[character_id]

    def get_mp(self) -> int:
        return self._current_mp

    def spend_mp(self, cost: int) -> bool:
        if self._current_mp >= cost:
            self._current_mp -= cost
            return True
        else:
            return False
