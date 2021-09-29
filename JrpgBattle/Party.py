from typing import List, Set, Dict, Callable

from JrpgBattle.Attack import AttackQueue
from JrpgBattle.Character import CharacterStatus

def redacted(func: Callable) -> Callable:
    def redacted(*args, **kwargs):


class Party:
    def __init__(self,
                 characters: Set[CharacterStatus]=[],  # the characters in the party
                 attack_queue: AttackQueue=AttackQueue(),  # the queue of attacks which the party will execute in the next turn
                 current_mp: int=0):  # the current mana points. MP is a shared resource
        self._characters = characters
        self._attack_queue = attack_queue
        self._current_mp = current_mp

    @property
    def __iter__(self):
        return self._characters.__iter__()

    def is_wiped_out(self) -> bool:
        for member in self._characters:
            if not member.is_dead():
                return False
        return True

    def get_mp(self) -> int:
        return self._current_mp

    def spend_mp(self, cost: int) -> bool:
        if self._current_mp >= cost:
            self._current_mp -= cost
            return True
        else:
            return False
