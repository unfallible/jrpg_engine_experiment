from __future__ import annotations
from enum import Enum, auto
from typing import TYPE_CHECKING
from JrpgBattle.BattleEventHandling.EventManagement import BattleEvent
from JrpgBattle.Character import CharacterStatus

if TYPE_CHECKING:
    from JrpgBattle.Attack import Attack


class AttackEventType(Enum):
    ATTACK_STARTED = auto()
    ATTACK_HIT = auto()
    ATTACK_PARRIED = auto()
    PAYMENT_FAILED = auto()
    ATTACK_STAGGERED = auto()


class AttackEvent(BattleEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 # attack,  # : Attack,
                 attack: Attack,
                 event_type: AttackEventType,
                 cause: BattleEvent = None):
        super().__init__(cause=cause)
        self.attacker = attacker  # the character using the attack
        self.attack = attack  # the attack being used
        self.event_type = event_type


class AttackStartedEvent(AttackEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 cause: BattleEvent = None):
        super().__init__(attacker,
                         attack,
                         AttackEventType.ATTACK_STARTED,
                         cause=cause)

    def __str__(self):
        return f'{self.attacker.character_name} uses their {self.attack.name} attack.'


class PaymentFailedEvent(AttackEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 cause: BattleEvent = None):
        super().__init__(attacker,
                         attack,
                         AttackEventType.PAYMENT_FAILED,
                         cause=cause)

    def __str__(self):
        return f'Not enough SP. {self.attacker.character_name}\'s {self.attack.name} attack is cancelled.'


class AttackStaggeredEvent(AttackEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 cause: BattleEvent = None):
        super().__init__(attacker,
                         attack,
                         AttackEventType.ATTACK_STAGGERED,
                         cause=cause)

    def __str__(self):
        return f'{self.attacker.character_name}\'s {self.attack.name} attack misses because they staggered.'


class ImpactEvent(AttackEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 target: CharacterStatus,
                 cause: BattleEvent = None):
        super().__init__(attacker, attack, AttackEventType.ATTACK_HIT, cause=cause)
        self.target = target
        self.event_type = AttackEventType.ATTACK_HIT


class ParryEvent(AttackEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 target: CharacterStatus,
                 defender: CharacterStatus,
                 cause: BattleEvent = None):
        super().__init__(attacker, attack, AttackEventType.ATTACK_PARRIED, cause=cause)
        self.target = target
        self.defender = defender

    def __str__(self):
        defense_target = 'themselves' if self.defender == self.target \
            else self.target.character_name
        return f'{self.defender.character_name} defends {defense_target} ' \
               f'from {self.attacker.character_name}'
