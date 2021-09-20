from enum import Enum
from fractions import Fraction
from typing import List, Callable, Set, Tuple

from JrpgBattle.Character import CharacterStatus, Multiplier, CharacterSheet


class Attack:
    def __init__(self,
                 name: str,
                 base_dmg_func: Callable[[AttackPlan, CharacterStatus], int]=lambda: 0,  # a function returning the attack's base damage
                 type: AttackType=AttackType.UTILITY,  # the elemental type of the attack
                 target_range: Tuple[int, int]=(1,1),  # the minimum and maximum (inclusive) number of characters the attack can target
                 action_point_cost: int=100,  #
                 stamina_point_cost: int=100,  #
                 mana_point_cost: int=0):  #
        self.name = name
        self.base_dmg_func = base_dmg_func
        self.type = type
        self.target_range = target_range
        self.action_point_cost = action_point_cost
        self.stamina_point_cost = stamina_point_cost
        self.mana_point_cost = mana_point_cost



class AttackType(Enum):
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


class AttackPlan:
    PENDING = 0
    CANCELLED = 1
    IN_PROGRESS = 2
    HIT = 3
    PARTIAL_HIT = 4
    MISS = 5
    SKIPPED = 6
    NO_TARGET = 7

    def __init__(self,
                 attack: Attack=None,
                 user: CharacterStatus=None,
                 targets: Set[CharacterStatus]=None,
                 status=PENDING):
        self.attack = attack
        self.user = user
        self.targets = targets
        self.status = status

    def execute(self):
        # if the attack was not cancelled then its status should be PENDING
        assert self.status == AttackPlan.PENDING or \
               self.status == AttackPlan.CANCELLED, "Invalid AttackPlan status"

        # start by checking that the attack is still scheduled
        if self.status == AttackPlan.CANCELLED:
            self.status = AttackPlan.SKIPPED
            return

        # Now process the payment for the attack
        payment_successful = self.user.attack_payment(self.attack.action_point_cost,
                                                      self.attack.stamina_point_cost,
                                                      self.attack.mana_point_cost)
        if not payment_successful:
            self.status = AttackPlan.SKIPPED
            return

        # TODO: Should there be any kind of lock here?
        self.status = AttackPlan.IN_PROGRESS # the AttackPlan is now executing
        result = AttackPlan.IN_PROGRESS # Assume the attack missed unless it hits
        for target in self.targets:
            # if the target is dead, update the result and continue looping over targets
            # Note that a missing target counts as neither a hit nor a miss
            if target.is_dead():
                result = AttackPlan.NO_TARGET if result == AttackPlan.IN_PROGRESS else result
                continue
            # since the attack is being used, mark the target as attacked
            target.set_was_attacked()

            # now check if the target parried
            parry_multiplier = Fraction(1, 1)
            if target.get_defender() is not None:
                parry_effectiveness = target.get_defender().get_parry_effectiveness()
                assist_penalty = Fraction(0) if target.get_defender() is target else Fraction(1, 2)
                parry_multiplier = 1 - (parry_effectiveness ** (assist_penalty + target._vulnerability))
                if result == AttackPlan.IN_PROGRESS or AttackPlan.NO_TARGET:  # IN_PROGRESS means this is the first target
                    result = AttackPlan.MISS
                elif result == AttackPlan.HIT:
                    result = AttackPlan.PARTIAL_HIT
            elif result == AttackPlan.IN_PROGRESS or AttackPlan.NO_TARGET:
                result = AttackPlan.HIT
            elif result == AttackPlan.MISS:
                result = AttackPlan.PARTIAL_HIT

            # if parry was perfect, just skip the rest of the attack calculations
            if parry_multiplier <= 0:
                continue

            #TODO: Consider optimizing multipliers
            total_multiplier = Fraction(1, 1)
            # aggregate offensive multipliers
            for multiplier in self.user.get_offensive_type_affinities():
                if multiplier.is_relevant(self):
                    total_multiplier *= multiplier
            # aggregate defensive multipliers
            for multiplier in target.get_defensive_type_affinities():
                if multiplier.is_relevant(self):
                    total_multiplier *= multiplier

            # calculate base damage
            base_damage = self.attack.base_dmg_func(self, target)

            total_damage = base_damage*total_multiplier*parry_multiplier
            target.receive_enemy_damage(total_damage)

        #after processing all targets, update the attack's status with the result
        self.status = result


class AttackQueue:
    def __init__(self,
                 entries: List[AttackPlan] = []):
        self._entries = entries
        self._max_sp_cost =

    @property
    def __iter__(self):
        return self._entries.__iter__()

    # Add a plan to the attack queue
    def enqueue(self, plan: AttackPlan):
        self._entries[len(self._entries)] = plan

    # Filter plans out of the attack queue and return a new, filtered version
    def filter_queue(self,
                     attack_filter: Callable[[AttackPlan], bool]) -> AttackQueue:
        return AttackQueue([plan for plan in self._entries if attack_filter(plan)])
