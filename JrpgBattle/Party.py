from typing import List, Dict

from JrpgBattle import Attack, Character


class Party:
    def __init__(self,
                 characters: List[CharacterStatus]=[],  # the characters in the party
                 attack_queue: Attack=Attack(),  # the queue of attacks which the party will execute in the next turn
                 current_mp: int=0):  # the current mana points. MP is a shared resource
        self.characters = characters
        self.parry_list = parry_list
        self.attack_queue = attack_queue
        self.current_mp = current_mp

    @property
    def __iter__(self):
        return self.characters.__iter__()

