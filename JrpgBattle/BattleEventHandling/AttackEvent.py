from typing import TYPE_CHECKING
from JrpgBattle.BattleEventHandling.EventManagement import BattleEvent
from JrpgBattle.Character import CharacterStatus

if TYPE_CHECKING:
    from JrpgBattle.Attack import Attack


class AttackEvent(BattleEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 cause: BattleEvent = None):
        super().__init__(cause=cause)
        self.attacker = attacker  # the character using the attack
        self.attack = attack  # the attack being used


class ImpactEvent(AttackEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 target: CharacterStatus,
                 cause: BattleEvent = None):
        super().__init__(attacker, attack, cause=cause)
        self.target = target


class ParryEvent(ImpactEvent):
    def __init__(self,
                 attacker: CharacterStatus,
                 attack,  # : Attack,
                 target: CharacterStatus,
                 defender: CharacterStatus,
                 cause: BattleEvent = None):
        super().__init__(attacker, attack, target, cause=cause)
        self.defender = defender

    def __str__(self):
        return f'{self.defender.character_name} defends {self.target.character_name} ' \
               f'from {self.attacker.character_name}'
