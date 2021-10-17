from __future__ import annotations

from copy import copy
from math import ceil
from typing import List, Callable, Set, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import IntEnum
from fractions import Fraction
from JrpgBattle.Character import CharacterStatus

from JrpgBattle.BattleEventHandling.AttackEvent import ParryEvent, AttackStartedEvent, PaymentFailedEvent, \
    AttackStaggeredEvent
from JrpgBattle.BattleEventHandling.EventManagement import notify_shared_observers


class AttackType(IntEnum):
    UTILITY = 0
    SLASH = 1
    STAB = 2
    STRIKE = 3
    FIRE = 4
    FIRE_SLASH = 5
    FIRE_STAB = 6
    FIRE_STRIKE = 7
    POISON = 8
    POISON_SLASH = 9
    POISON_STAB = 10
    POISON_STRIKE = 11
    POISON_FIRE = 12
    POISON_FIRE_SLASH = 13
    POISON_FIRE_STAB = 14
    POISON_FIRE_STRIKE = 15

    @staticmethod
    def is_utility(attack_type: AttackType) -> bool:
        return attack_type == 0

    @staticmethod
    def is_slash(attack_type: AttackType) -> bool:
        return (attack_type % 4) == 1

    @staticmethod
    def is_stab(attack_type: AttackType) -> bool:
        return (attack_type % 4) == 2

    @staticmethod
    def is_strike(attack_type: AttackType) -> bool:
        return (attack_type % 4) == 3

    @staticmethod
    def is_physical(attack_type: AttackType) -> bool:
        return (attack_type % 4) != 0

    @staticmethod
    def is_fire(attack_type: AttackType) -> bool:
        return (attack_type & 4) == 1

    @staticmethod
    def is_poison(attack_type: AttackType) -> bool:
        return (attack_type & 8) == 1


class Attack(ABC):
    def __init__(self,
                 name: str,
                 attack_type: AttackType=AttackType.UTILITY,  # the elemental event_type of the attack
                 target_range: Tuple[int, int]=(1, 1),  # the minimum and maximum (inclusive) number of characters the attack can target
                 stamina_point_cost: int=100,
                 hiddenness: int = CharacterStatus.VISIBLE_MEDIUM,
                 reveal: int = CharacterStatus.VISIBLE_MEDIUM):
        self.name = name
        self.attack_type = attack_type
        self.target_range = target_range
        self.stamina_point_cost = stamina_point_cost
        self.hiddenness = hiddenness
        self.reveal = reveal

    def __repr__(self):
        return self.name

    def get_name(self) -> str:
        return self.name

    def __eq__(self, other):
        return isinstance(other, Attack) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def get_attack_type(self) -> AttackType:
        return self.attack_type

    def get_target_range(self) -> Tuple[int, int]:
        return self.target_range

    def get_sp_cost(self) -> int:
        return self.stamina_point_cost

    @abstractmethod
    def get_power(self) -> str:
        pass

    @abstractmethod
    def compute_base_damage(self,
                            plan: DetailedAttackPlan,
                            target: CharacterStatus) -> int:
        pass


class AttackPlan:
    def __init__(self,
                 user: CharacterIdentifier,
                 attack: Attack,
                 targets: Set[CharacterIdentifier]):
        self.user = user
        self.attack = attack
        self.targets = targets

    def __repr__(self):
        return f'{repr(self.user)}, {repr(self.attack)}, {repr(self.targets)}'


class VanillaAttack(Attack):
    def __init__(self,
                 name: str,
                 attack_type: AttackType = AttackType.UTILITY,  # the elemental event_type of the attack
                 # the minimum and maximum (inclusive) number of characters the attack can target
                 target_range: Tuple[int, int] = (1, 1),
                 stamina_point_cost: int = 100,  #
                 damage: int = 0):
        super().__init__(name=name,
                         attack_type=attack_type,
                         target_range=target_range,
                         stamina_point_cost=stamina_point_cost)
        self.damage = damage

    def compute_base_damage(self,
                            plan: DetailedAttackPlan,
                            target: CharacterStatus) -> int:
        return self.damage

    def get_power(self) -> str:
        return str(self.damage)


class DetailedAttackPlan:
    PENDING = 0
    CANCELLED = 1
    IN_PROGRESS = 2
    HIT = 3
    PARTIAL_HIT = 4
    MISS = 5
    SKIPPED = 6
    NO_TARGET = 7

    def __init__(self,
                 attack: Attack = None,
                 user: CharacterStatus = None,
                 targets: Set[CharacterStatus] = None,
                 status=PENDING):
        self.attack = attack
        self.user = user
        self.targets = targets
        self.status = status

    def __repr__(self):
        return f'{repr(self.user)}, {repr(self.attack)}, {repr(self.targets)}'

    def execute(self):
        # TODO EVENT
        self.user.publicize_attack(self.attack)

        # if the attack was not cancelled then its status should be PENDING
        assert self.status == DetailedAttackPlan.PENDING or \
               self.status == DetailedAttackPlan.CANCELLED, "Invalid DetailedAttackPlan status"

        # start by checking that the attack is still scheduled
        if self.status == DetailedAttackPlan.CANCELLED:
            self.status = DetailedAttackPlan.SKIPPED
            return

        attack_event = AttackStartedEvent(self.user, self.attack)
        self.user.notify_observers(attack_event)

        # Now process the payment for the attack
        payment_successful = self.user.attack_payment(self.attack.stamina_point_cost)
        if not payment_successful:
            attack_event = PaymentFailedEvent(self.user, self.attack)
            self.user.notify_observers(attack_event)
            self.status = DetailedAttackPlan.SKIPPED
            return

        self.user.used_attack = True
        # TODO THREADS: Should there be any kind of lock here?
        self.status = DetailedAttackPlan.IN_PROGRESS  # the DetailedAttackPlan is now executing
        swings = 0  # the number of targets the attack has been used against
        hits = 0  # the number of targets the attack has hit
        for target in self.targets:
            # if the target is dead, update the result and continue looping over targets
            # Note that a missing target counts as neither a hit nor a miss
            if target.is_dead():
                continue
            # since the attack is being used, mark the target as attacked
            target.set_was_attacked()
            swings += 1

            # if the user is staggered, their attack will fail
            """ TODO: putting this check here means that if a defended character is targeted by a staggered character,
            then the defending character doesn't get penalized for not getting attacked. 
            Putting the check up top might allow deeper reads, but also might be more frustrating. 
            What's the right choice? """
            if self.user.character_state == CharacterStatus.STAGGERED:
                attack_event = AttackStaggeredEvent(self.user, self.attack)
                self.user.notify_observers(attack_event)
                self.status = DetailedAttackPlan.MISS
                continue


            # now check if the target is being defended
            parry_multiplier = Fraction(1, 1)
            if target.get_defender() is None:
                # TODO EVENT: Attack hit
                hits += 1
                target.raise_visibility(self.attack.reveal)
            else:
                defender = target.get_defender()
                parry_effectiveness = defender.get_parry_effectiveness()
                parry_multiplier = (1 - defender.guard) ** float(parry_effectiveness)
                parry_event = ParryEvent(self.user,
                                         self.attack,
                                         target,
                                         defender)
                notify_shared_observers(parry_event,
                                        self.user,
                                        target,
                                        defender)

            # if parry was perfect, just skip the rest of the attack calculations
            if parry_multiplier <= 0:
                continue

            # calculate base damage
            base_damage = self.attack.compute_base_damage(self, target)

            total_damage = ceil(base_damage*parry_multiplier)
            target.receive_enemy_damage(total_damage)

        #after processing all targets, update the attack's status with the result
        if swings == 0:
            self.status = DetailedAttackPlan.NO_TARGET
        elif hits == 0:
            self.status = DetailedAttackPlan.MISS
        elif hits == swings:
            self.status = DetailedAttackPlan.HIT
        else:
            self.status = DetailedAttackPlan.PARTIAL_HIT


class AttackQueue:
    def __init__(self,
                 entries: List[DetailedAttackPlan] = []):
        self.entries = copy(entries)

    def __iter__(self):
        return self.entries.__iter__()

    # Add a plan to the attack queue
    def enqueue(self, plan: DetailedAttackPlan):
        # self.entries[len(self.entries)] = plan
        self.entries.append(plan)

    # Filter plans out of the attack queue and return a new, filtered version
    def filter_queue(self,
                     attack_filter: Callable[[DetailedAttackPlan], bool]) -> AttackQueue:
        return AttackQueue([plan for plan in self.entries if attack_filter(plan)])
