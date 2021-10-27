from __future__ import annotations
from typing import Callable, Set, TYPE_CHECKING, MutableSet
from copy import copy
from fractions import Fraction

from JrpgBattle.BattleEventHandling.CharacterUpdateEvent import UpdateType, CharacterUpdateEvent
from JrpgBattle.BattleEventHandling.EventManagement import BattleEvent, EventSubject
from JrpgBattle.IdentifierSet import Identifier

if TYPE_CHECKING:
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
    STANDBY = 0
    USED_ATTACK = 1
    STAGGERED = 2
    DEAD = 3

    VISIBILITY_PRIVATE = 0
    VISIBILITY_LOW = 1
    VISIBLE_MEDIUM = 2
    VISIBILITY_HIGH = 3
    VISIBILITY_PUBLIC = 4

    DEFENSE_PUBLIC = 0
    DEFENSE_PRIVATE = 1

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
        self.current_hp = current_hp if current_hp is not None else character.get_max_hp()
        self.current_sp: int = 0
        self.sp_spent: int = 0
        self.guard: Fraction = Fraction(1)
        self.was_attacked: bool = False  # This flag is set when a character is attacked. Resets at end of turn
        self.used_attack: bool = False
        self.is_defending: CharacterStatus = None  # The character this one is defending; 'None' if not parrying
        self.defended_by: CharacterStatus = None  # The character defending this one; 'None' if undefended
        self.public_attack_list: MutableSet[Attack] = set()
        self.character_state: int = CharacterStatus.STANDBY
        # describes whether the defense is publicised as soon as it's chosen or only after it's needed (e.g. when the defense target is attacked)
        self.defense_visibility: int = CharacterStatus.DEFENSE_PUBLIC
        # The values regulating the Character's next attack and its visibility
        self.visibility: int = CharacterStatus.VISIBILITY_PRIVATE
        self.next_plan: DetailedAttackPlan = None

    def get_character_name(self) -> str:
        return self.character_name

    def publicize_attack(self, attack: Attack):
        assert attack in self.attack_list
        self.public_attack_list.add(attack)

    def get_public_attack_list(self) -> Set[Attack]:
        return set(self.public_attack_list)

    def get_current_hp(self) -> int:
        return self.current_hp

    def get_guard(self) -> Fraction:
        return self.guard

    def set_defense(self, target: CharacterStatus):
        target.defended_by = self
        self.is_defending = target

    def is_defense_known(self) -> bool:
        defense_target = self.is_defending
        return self.defense_visibility == CharacterStatus.DEFENSE_PUBLIC \
               or (self.is_defending is not None and defense_target.was_attacked)

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
            self.character_state = CharacterStatus.DEAD
            event = CharacterUpdateEvent(self, UpdateType.CHARACTER_DIED, character_died=True)
            self.notify_observers(event)

    def set_plan(self, plan: DetailedAttackPlan) -> bool:
        if self.next_plan is not None:
            return False
        if plan.user is not self:
            return False
        if plan.attack not in self.attack_list:
            return False
        self.next_plan = plan
        return True

    def raise_visibility(self, visibility: int) -> int:
        assert CharacterStatus.VISIBILITY_PRIVATE <= visibility <= CharacterStatus.VISIBILITY_PUBLIC
        self.visibility = max(self.visibility, visibility)
        return self.visibility

    def next_known_attack(self) -> Attack:
        if self.next_plan is None:
            return None
        next_attack = self.next_plan.attack
        if next_attack.hiddenness <= self.visibility:
            return next_attack
        else:
            return None

    def is_dead(self) -> bool:
        return self.character_state == CharacterStatus.DEAD

    # this function performs basic character upkeep at the start of the turn
    def start_turn(self):
        # first, check for any failed parries.
        if self.defended_by is not None:
            if self.was_attacked:
                battle_event = CharacterUpdateEvent(self,
                                                    UpdateType.GUARD_RESET,
                                                    guard_reset=True)
                self.notify_observers(battle_event)
                self.guard = Fraction(1)
            else:
                battle_event = CharacterUpdateEvent(self,
                                                    UpdateType.GUARD_DROPPED,
                                                    guard_drop=Fraction(1, 2))
                self.notify_observers(battle_event)
                self.guard *= Fraction(1, 2)
        elif not self.was_attacked:
            battle_event = CharacterUpdateEvent(self,
                                                UpdateType.GUARD_RESET,
                                                guard_reset=True)
            self.notify_observers(battle_event)
            self.guard = Fraction(1)

        if self.is_defending is not None and not self.is_defending.was_attacked:
            self.character_state = CharacterStatus.STAGGERED
            stagger_event = CharacterUpdateEvent(self,
                                                 UpdateType.DEFENSE_WHIFFED,
                                                 character_staggers=True)
            self.notify_observers(stagger_event)
        self.sp_spent = 0

    # this function performs basic character upkeep between the execution and planning stages
    def turn_interval(self):
        # calculate sp reduction
        self.current_sp -= self.sp_spent

        # staggered characters don't get stamina points
        if self.character_state == CharacterStatus.STANDBY and not self.used_attack:
            self.current_sp += 100
            if self.character_state == CharacterStatus.STANDBY:
                event = CharacterUpdateEvent(self, UpdateType.SP_GAINED, sp_change=100)
                self.notify_observers(event)

        self.visibility = CharacterStatus.VISIBILITY_PRIVATE
        self.next_plan = None
        self.used_attack = False
        self.is_defending = None
        self.defended_by = None
        if self.character_state != CharacterStatus.DEAD:
            self.character_state = CharacterStatus.STANDBY

    # this function performs basic character upkeep at the end of the turn
    def end_turn(self):
        self.was_attacked = False
        if self.is_defending is not None and self.defense_visibility == CharacterStatus.DEFENSE_PUBLIC:
            event = CharacterUpdateEvent(self, UpdateType.DEFENSE_SET, defense_target=self.is_defending)
            self.notify_observers(event)

    def attack_payment(self, sp_cost: int) -> bool:
        if self.current_sp < sp_cost:
            return False
        else:
            self.sp_spent = max(self.sp_spent, sp_cost)
            event = CharacterUpdateEvent(self, UpdateType.SP_SPENT, sp_change=-1 * self.sp_spent)
            self.notify_observers(event)
            return True


class Multiplier(Fraction):
    def __init__(self,
                 multiplier: Fraction,
                 is_relevant: Callable[[DetailedAttackPlan], bool]):
        Fraction.__init__(multiplier)
        self.is_relevant = is_relevant
