from typing import Dict, Set

from JrpgBattle.Character import CharacterIdentifier, CharacterStatus
from JrpgBattle.IdentifierSet import IdentifierSet
from JrpgBattle.Party import Party, PartyIdentifier
from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView


class Environment:
    def __init__(self):
        self.turn: int = 0
        self.round: int = 0
        self.team: Set[PrivatePartyView] = set()
        self.team: Set[PublicPartyView] = set()
        self.characters_ids: IdentifierSet[CharacterStatus] = {}
        self.party_ids: IdentifierSet[Party] = {}

    def register_party(self, party: Party) -> bool:
        if party.characters & self.characters_ids:
            return False
        self.roster.append(new_player)
        self.party_ids[party] = party
        # TODO: Find better way to add the character ids
        for character in party:
            self.characters_ids[character] = character
        return BattleClient.SUCCESS
