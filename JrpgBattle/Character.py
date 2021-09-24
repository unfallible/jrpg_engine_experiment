from __future__ import annotations
from typing import Callable, Set, TYPE_CHECKING
from copy import copy
from fractions import Fraction

#from JrpgBattle import Party
if TYPE_CHECKING:
    from JrpgBattle.Attack import Attack, AttackPlan, AttackQueue, AttackType

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
                 attack_list: Set[Attack]={},
                 parry_effectiveness: Fraction=Fraction(1)):
        # variables describing the character's current profile
        self._name = name
        self._max_hp = max_hp
        self._offensive_type_affinities = offensive_type_affinities
        self._defensive_type_affinities = defensive_type_affinities
        self._attack_list = attack_list
        self._parry_effectiveness = parry_effectiveness

    def get_name(self):
        return self._name

    def get_max_hp(self):
        return self._max_hp

    def get_offensive_type_affinities(self) -> Set[Multiplier]:
        return copy(self._offensive_type_affinities)

    def get_defensive_type_affinities(self) -> Set[Multiplier]:
        return copy(self._defensive_type_affinities)

    def get_attack_list(self) -> Set[Attack]:
        return copy(self._attack_list)

    def get_parry_effectiveness(self) -> Fraction:
        return self._parry_effectiveness


class CharacterStatus(CharacterSheet):
    def __int__(self,
                character: CharacterSheet,
                party: Party,
                current_hp: int=None):
        CharacterSheet.__init__(self,
                                character.get_name(),
                                character.get_max_hp(),
                                character.get_offensive_type_affinities(),
                                character.get_defensive_type_affinities(),
                                character.get_attack_list(),
                                character.get_parry_effectiveness())
        self._party = party
        self._current_hp = current_hp if current_hp is not None else character.get_max_hp()
        self._current_sp: int = 0
        self._sp_spent: int = 0
        self._current_ap: int = 0
        self._stagger: bool = False  # This flag is set when a character is staggered. Resets mid-turn
        self._vulnerability: int = 0
        self._was_attacked: bool = False  # This flag is set when a character is attacked. Resets at end of turn
        self._is_defending: CharacterStatus = None  # The character this one is defending; 'None' if not parrying
        self._defended_by: CharacterStatus = None  # The character defending this one; 'None' if undefended
        # TODO: add functionality for death
        self._dead: bool = False

    def get_vulnerability(self) -> int:
        return self._vulnerability

    def get_defender(self) -> CharacterStatus:
        return self._defended_by

    def set_was_attacked(self):
        self._was_attacked = True

    def receive_enemy_damage(self, damage: int):
        self._current_hp -= damage
        if self._current_hp <= 0:
            self._current_hp = 0
            self._dead = True

    def is_dead(self) -> bool:
        return self._dead

    # this function performs basic character upkeep at the start of the turn
    def start_turn(self):
        # first, check for any failed parries.
        if self._defended_by is not None:
            if self._was_attacked:
                self._vulnerability = 0
            else:
                self._vulnerability += 1
                self._stagger = True
        elif not self._was_attacked:
            self._vulnerability = 0

        self._current_ap = 100
        self._sp_spent = 0

    # this function performs basic character upkeep between the execution and planning stages
    def turn_interval(self):
        # calculate sp reduction
        self._current_sp -= self._sp_spent

        # staggered characters don't get stamina points
        if not self._stagger:
            self._current_sp += self._current_ap

        self._is_defending = None
        self._defended_by = None
        self._stagger = False

    # this function performs basic character upkeep at the end of the turn
    def end_turn(self):
        self._was_attacked = False

    def attack_payment(self, ap_cost: int, sp_cost: int, mp_cost: int) -> bool:
        if self._current_ap < ap_cost:
            return False
        elif self._current_sp <= 0:
            return False
        elif self._party.get_mp() < mp_cost:
            return False
        else:
            self._current_ap -= ap_cost
            self._sp_spent = max(self._sp_spent, sp_cost)
            self._party.spend_mp(mp_cost)
            return True

class Multiplier(Fraction):
    def __init__(self,
                 multiplier: Fraction,
                 is_relevant: Callable[[AttackPlan], bool]):
        Fraction.__init__(multiplier)
        self.is_relevant = is_relevant
