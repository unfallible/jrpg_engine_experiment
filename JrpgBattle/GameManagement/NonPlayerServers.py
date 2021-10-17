import random
from typing import List, Tuple

from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.CharacterViews import PrivateCharacterView, PublicCharacterView
from JrpgBattle.GameManagement.MainBattleClient import PlayerServer, BattleClient
from JrpgBattle.Party import Party
from JrpgBattle.Attack import Attack, AttackPlan


class AggroNonPlayerServer(PlayerServer):
    def __init__(self, attack_chance: float = 1.0, defense_chance: float = 0):
        self.attack_chance = attack_chance
        self.defense_chance = defense_chance
        self.team: PrivatePartyView = PrivatePartyView(Party(""))
        self.enemy: PublicPartyView = PublicPartyView(Party(""))
        self.team_index: List[Tuple[PrivateCharacterView, List[Attack]]] = []
        self.enemy_index: List[PublicCharacterView] = []

    def process_command_request(self,
                                client: BattleClient,
                                transaction_id: int,
                                team: PrivatePartyView,
                                enemy: PublicPartyView):
        client_rval = BattleClient.ERROR
        while client_rval == BattleClient.ERROR:
            attacks: List[AttackPlan] = []
            defenses = {}
            for character in team:
                target = next(iter(enemy))
                if character.get_sp() == 0 or random.random() < (1.0 - self.attack_chance):
                    continue
                attacks.append(AttackPlan(character,
                                          next(iter(character.get_attack_list())),
                                          {target}))
                if target.get_sp() > 0 and random.random() < self.defense_chance:
                    defenses[character] = character
            client_rval = client.process_command_response(attacks=attacks, defenses=defenses, transaction_id=transaction_id)
        return PlayerServer.SUCCESS
