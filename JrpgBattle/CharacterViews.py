from typing import Set, TYPE_CHECKING
from fractions import Fraction
from copy import copy
from JrpgBattle.Attack import Attack
from JrpgBattle.Character import CharacterStatus, Multiplier, CharacterIdentifier
if TYPE_CHECKING:
    from JrpgBattle.Party import Party


class RedactedError(Exception):
    pass


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
    def __init__(self, character: CharacterStatus):
        super(PublicCharacterView, self).__init__(character.character_name)
        self._character = character

    def get_character_name(self) -> str:
        return self._character.character_name

    def get_guard(self) -> Fraction:
        return self._character.guard

    def get_damage(self) -> int:
        return self._character.get_max_hp() - self._character.get_current_hp()

    def get_sp(self) -> int:
        return self._character.current_sp

    def get_sp_spent(self) -> int:
        return self._character.sp_spent

    def get_public_attack_list(self) -> Set[Attack]:
        return copy(self._character.get_public_attack_list())

    def is_defense_known(self) -> bool:
        return self._character.is_defense_known()

    def get_is_defending(self) -> CharacterStatus:
        if not self.is_defense_known():
            raise RedactedError()
        return self._character.is_defending

    def was_attacked(self) -> bool:
        return self._character.was_attacked

    def is_staggered(self) -> bool:
        return self._character.character_state == CharacterStatus.STAGGERED

    def get_next_attack(self) -> Attack:
        return self._character.next_known_attack()

    def get_visibility(self) -> int:
        return self._character.visibility

    def is_dead(self) -> bool:
        return self._character.is_dead()


class PrivateCharacterView(PublicCharacterView):
    def __init__(self, character: CharacterStatus):
        PublicCharacterView.__init__(self, character)
        # self._character = character

    def get_template_name(self) -> str:
        return self._character.template_name

    def get_max_hp(self) -> int:
        return self._character.max_hp

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
