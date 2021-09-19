from fractions import Fraction
from typing import Callable, Set
from JrpgBattle.Attack import Attack, AttackPlan

"""
The CharacterSheet descibes the profile of a character without reference
to the character's state in a particular battle. It is used to construct
CharacterStatus objects for battles. This has certain advantages, such as
allowing common enemies to be repeatedly built from the same template.

"""


class CharacterSheet:
    def __init__(self,
                 name: str,
                 max_hp: int,
                 offensive_type_affinities: Set[Multiplier]={},
                 defensive_type_affinities: Set[Multiplier]={},
                 attack_list: Set[Attack]=[],
                 parry_effectiveness: Fraction=Fraction(1, 1)):
        # variables describing the character's current profile
        self.name = name
        self.max_hp = max_hp
        self.offensive_type_affinities = offensive_type_affinities
        self.defensive_type_affinities = defensive_type_affinities
        self.attack_list = attack_list
        self.parry_effectiveness = parry_effectiveness


class CharacterStatus(CharacterSheet):
    def __int__(self,
                character: CharacterSheet=None,
                current_hp: int=None):
        self.current_hp = character.max_hp
        self.current_sp: int = 0
        self.current_ap: int = 0
        self.stagger: bool = False  # This flag is set when a character is staggered. Resets mid-turn
        self.vulnerability: int = 0
        self.was_attacked: bool = False  # This flag is set when a character is attacked. Resets at end of turn
        self.is_defending: CharacterStatus = None  # The character this one is defending, if any, or 'None'
        self.defended_by: CharacterStatus = None

    def start_turn(self):
        # first, check for any failed parries.
        if self.defended_by is not None:
            if self.was_attacked:
                self.vulnerability = 0
            else:
                self.vulnerability += 1
                self.stagger = True
        elif not self.was_attacked:
            self.vulnerability = 0

        self.current_ap = 100

    def turn_interval(self):
        if not self.stagger:
            self.current_sp += self.current_ap
        self.is_defending = None
        self.defended_by = None
        self.stagger = False

    def end_turn(self):
        self.was_attacked = False


class Multiplier(Fraction):
    def __init__(self,
                 multiplier: Fraction,
                 is_relevant: Callable[[AttackPlan], bool]):
        Fraction.__init__(multiplier)
        self.is_relevant = is_relevant
