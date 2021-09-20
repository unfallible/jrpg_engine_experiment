from typing import List, Dict

from JrpgBattle import Attack, Character
from JrpgBattle.Character import CharacterStatus


class Party:
    def __init__(self,
                 characters: List[CharacterStatus]=[],  # the characters in the party
                 attack_queue: Attack=Attack(),  # the queue of attacks which the party will execute in the next turn
                 current_mp: int=0):  # the current mana points. MP is a shared resource
        self.characters = characters
        self.attack_queue = attack_queue
        self.current_mp = current_mp

    @property
    def __iter__(self):
        return self.characters.__iter__()

    def is_wiped_out(self) -> bool:
        for member in self.characters:
            if not member.is_dead():
                return False
        return True

    def get_mp(self) -> int:
        return self.current_mp

    def spend_mp(self, cost: int) -> bool:
        if self.current_mp >= cost:
            self.current_mp -= cost
            return True
        else:
            return False
