from typing import Set, TYPE_CHECKING
from fractions import Fraction
from copy import copy
from JrpgBattle.Character import CharacterStatus, Multiplier, CharacterIdentifier
if TYPE_CHECKING:
    from JrpgBattle.Attack import Attack
    from JrpgBattle.Party import Party


class PublicCharacterView(CharacterIdentifier):
    """
    PublicCharacterView objects provide views of CharacterStatus objects
    without methods for easily modifying them. Its interface also provides
    methods which only allow access to the features of the viewed object
    which are viewable by all players. This view is mainly intended to be
    sent to PlayerServer objects to allow them to keep track of the game state
    and send orders to the BattleClient. The PublicCharacterView is the most
    restrictive view. However, it can be extended to create more permissive
    views as well.
    """
    def __int__(self, character: CharacterStatus):
        self._character = character

    def get_character_name(self) -> str:
        return self._character.character_name

    def get_party(self) -> Party:
        return self._character.party

    def get_vulnerability(self) -> int:
        return self._character.get_vulnerability()

    def get_damage(self) -> int:
        return self._character.get_max_hp() - self._character.get_current_hp()

    def get_sp(self) -> int:
        return self._character.current_sp

    def get_sp_spent(self) -> int:
        return self._character.sp_spent

    def get_ap(self) -> int:
        return self._character.current_ap

    def get_public_attack_list(self) -> Set[Attack]:
        return copy(self._character.get_public_attack_list())

    def get_public_offensive_multipliers(self) -> Set[Multiplier]:
        return self._character.public_offensive_multipliers

    def get_public_defensive_multipliers(self) -> Set[Multiplier]:
        return self._character.public_defensive_multipliers

    def was_attacked(self) -> bool:
        return self._character.was_attacked

    def is_staggered(self) -> bool:
        return self._character.stagger

    def is_dead(self) -> bool:
        return self._character.is_dead()


class PrivateCharacterView(PublicCharacterView):
    def __init__(self, character: CharacterStatus):
        super().__init__(character)

    def get_template_name(self) -> str:
        return self._character.template_name

    def get_max_hp(self) -> int:
        return self._character.max_hp

    def get_offensive_multipliers(self) -> Set[Multiplier]:
        return self._character.offensive_type_affinities

    def get_defensive_multipliers(self) -> Set[Multiplier]:
        return self._character.defensive_type_affinities

    def get_attack_list(self) -> Set[Attack]:
        return self._character.attack_list

    def get_parry_effectiveness(self) -> Fraction:
        return self._character.parry_effectiveness

    def get_current_hp(self) -> int:
        return self._character.current_hp

    def get_is_defending(self) -> CharacterStatus:
        return self._character.is_defending

    def get_defended_by(self) -> CharacterStatus:
        return self._character.defended_by
