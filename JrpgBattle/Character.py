from __future__ import annotations
from typing import Callable, Set, TYPE_CHECKING, MutableSet
from copy import copy
from fractions import Fraction

from JrpgBattle.BattleEventHandling.CharacterUpdateEvent import UpdateType, CharacterUpdateEvent
from JrpgBattle.BattleEventHandling.EventManagement import BattleEvent, EventSubject
from JrpgBattle.IdentifierSet import Identifier

if TYPE_CHECKING:
    from JrpgBattle.Party import Party
    from JrpgBattle.Attack import Attack, DetailedAttackPlan

"""
The CharacterTemplate describes the profile of a character without reference
to the character's state in a particular battle. It is used to construct
CharacterStatus objects for battles. This has certain advantages, such as
allowing common enemies to be repeatedly built from the same template.

"""


class CharacterTemplate:
    def __init__(self,
                 name: str,
                 max_hp: int,
                 attack_list: Set[Attack] = frozenset(),
                 parry_effectiveness: Fraction = Fraction(1)):
        # variables describing the character's current profile
        self.template_name = name
        self.max_hp = max_hp
        self.attack_list = attack_list
        self.parry_effectiveness = parry_effectiveness

    def get_template_name(self):
        return self.template_name

    def get_max_hp(self) -> int:
        return self.max_hp

    def get_attack_list(self) -> Set[Attack]:
        return copy(self.attack_list)

    def get_parry_effectiveness(self) -> Fraction:
        return self.parry_effectiveness


class CharacterIdentifier(Identifier):
    DOMAIN: str = "character"

    def __init__(self, name: str):
        super().__init__(name)

    def get_domain(self) -> object:
        return CharacterIdentifier.DOMAIN


class CharacterStatus(CharacterTemplate, CharacterIdentifier, EventSubject[BattleEvent]):
    def __init__(self,
                 character: CharacterTemplate,
                 name: str,
                 # party: Party,
                 current_hp: int = None):
        CharacterIdentifier.__init__(self, name)
        EventSubject.__init__(self)
        CharacterTemplate.__init__(self,
                                   character.get_template_name(),
                                   character.get_max_hp(),
                                   character.get_attack_list(),
                                   character.get_parry_effectiveness())
        self.character_name = name
        # self.party = party
        self.current_hp = current_hp if current_hp is not None else character.get_max_hp()
        self.current_sp: int = 0
        self.sp_spent: int = 0
        self.current_ap: int = 0
        self.stagger: bool = False  # This flag is set when a character is staggered. Resets mid-turn
        self.vulnerability: int = 0
        self.was_attacked: bool = False  # This flag is set when a character is attacked. Resets at end of turn
        self.is_defending: CharacterStatus = None  # The character this one is defending; 'None' if not parrying
        self.defended_by: CharacterStatus = None  # The character defending this one; 'None' if undefended
        self.public_attack_list: MutableSet[Attack] = set()
        # TODO: add functionality for death
        self.dead: bool = False

    def get_character_name(self) -> str:
        return self.character_name

    def publicize_attack(self, attack: Attack):
        assert attack in self.attack_list
        self.public_attack_list.add(attack)

    def get_public_attack_list(self) -> Set[Attack]:
        return set(self.public_attack_list)

    def get_current_hp(self) -> int:
        return self.current_hp

    def get_vulnerability(self) -> int:
        return self.vulnerability

    def set_defense(self, target: CharacterStatus):
        target.defended_by = self
        self.is_defending = target

    def get_defender(self) -> CharacterStatus:
        return self.defended_by

    def set_was_attacked(self):
        self.was_attacked = True

    def receive_enemy_damage(self, damage: int):
        self.current_hp -= damage
        event = CharacterUpdateEvent(self, UpdateType.DAMAGE_INCURRED, hp_change=damage)
        self.notify_observers(event)
        if self.current_hp <= 0:
            self.current_hp = 0
            self.dead = True
            event = CharacterUpdateEvent(self, UpdateType.CHARACTER_DIED, character_died=True)
            self.notify_observers(event)

    def is_dead(self) -> bool:
        return self.dead

    # this function performs basic character upkeep at the start of the turn
    def start_turn(self):
        # first, check for any failed parries.
        if self.defended_by is not None:
            if self.was_attacked:
                battle_event = CharacterUpdateEvent(self,
                                                    UpdateType.VULNERABILITY_RESET,
                                                    vulnerability_change=-1*self.vulnerability)
                self.notify_observers(battle_event)
                self.vulnerability = 0
            else:
                battle_event = CharacterUpdateEvent(self,
                                                    UpdateType.VULNERABILITY_RAISED,
                                                    vulnerability_change=1)
                self.notify_observers(battle_event)
                self.vulnerability += 1
        elif not self.was_attacked:
            battle_event = CharacterUpdateEvent(self,
                                                UpdateType.VULNERABILITY_RESET,
                                                vulnerability_change=-1 * self.vulnerability)
            self.notify_observers(battle_event)
            self.vulnerability = 0

        if self.is_defending is not None and not self.is_defending.was_attacked:
            self.stagger = True
            stagger_event = CharacterUpdateEvent(self,
                                                 UpdateType.DEFENSE_WHIFFED,
                                                 character_staggers=True)
            self.notify_observers(stagger_event)
        self.current_ap = 100
        self.sp_spent = 0

    # this function performs basic character upkeep between the execution and planning stages
    def turn_interval(self):
        # calculate sp reduction
        self.current_sp -= self.sp_spent

        # staggered characters don't get stamina points
        if not self.stagger:
            self.current_sp += self.current_ap
            if self.current_ap > 0:
                event = CharacterUpdateEvent(self, UpdateType.SP_GAINED, sp_change=self.current_ap)
                self.notify_observers(event)

        self.is_defending = None
        self.defended_by = None
        self.stagger = False

    # this function performs basic character upkeep at the end of the turn
    def end_turn(self):
        self.was_attacked = False

    def attack_payment(self, ap_cost: int, sp_cost: int) -> bool:
        if self.current_ap < ap_cost:
            return False
        elif self.current_sp <= 0:
            return False
        else:
            self.current_ap -= ap_cost
            self.sp_spent = max(self.sp_spent, sp_cost)
            event = CharacterUpdateEvent(self, UpdateType.SP_SPENT, sp_change=-1*self.sp_spent)
            self.notify_observers(event)
            # self.party.spend_mp(mp_cost)
            return True


class Multiplier(Fraction):
    def __init__(self,
                 multiplier: Fraction,
                 is_relevant: Callable[[DetailedAttackPlan], bool]):
        Fraction.__init__(multiplier)
        self.is_relevant = is_relevant
