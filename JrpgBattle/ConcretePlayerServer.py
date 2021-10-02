from typing import Dict, List, Tuple
from abc import ABC, abstractmethod

from JrpgBattle.Character import CharacterStatus
from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.CharacterViews import PrivateCharacterView, PublicCharacterView
from JrpgBattle.MainBattleClient import PlayerServer, BattleClient
from JrpgBattle.Party import PartyIdentifier, Party
from JrpgBattle.Attack import Attack


class InteractivePlayerServer(PlayerServer):
    def __init__(self, client: BattleClient):
        self.team: PrivatePartyView = PrivatePartyView(Party(""))
        self.enemy: PublicPartyView = PublicPartyView(Party(""))
        self.team_index: List[Tuple[PrivateCharacterView, List[Attack]]] = []
        self.enemy: List[PublicCharacterView] = []
        self.open_request: bool = False

    def process_action_request(self,
                               client: BattleClient,
                               party_id: PartyIdentifier,
                               transaction_id: int):
        pass

    def process_team_response(self,
                              team: PrivatePartyView,
                              transaction_id: int) -> int:
        self.team = team
        self.team_index = [(char, [atk for atk in char.get_attack_list()]) for char in team]
        # for char in team:
        #     self.team_index.append((char, [atk for atk in char.get_attack_list()]))
        self.open_request = False
        return PlayerServer.SUCCESS

    def process_enemy_response(self,
                               enemy: PublicPartyView,
                               transaction_id: int) -> int:
        self.enemy = enemy
        self.open_request = False
        return PlayerServer.SUCCESS

    def _print_player_view(self, team: PrivatePartyView, enemy: PublicPartyView):
        print(f'Team {team.name[:8]}:')
        ci = 1
        for c in team:
            # the nested f string concatenates 'ci' with '.' and then left justifies it
            print(f'{f"{ci}.":<{3}}  {c.get_character_name()[:8]:<{8}} '
                  f'HP: {f"{c.get_current_hp()}/{c.get_max_hp()}":<{8}} '
                  f'SP: {c.get_sp():<+{3}}')
            ai = 1
            for a in c.get_attack_list():
                print(f'    {ai:>{2}}.  {a.name[:8]:<{8}} STR: SP:{a.stamina_point_cost:<+{3}}')
                ai += 1
            ci += 1
        print('ENEMIES:')
        for c in enemy:
            print(f'{f"{ci}.":<{3}}  {c.get_character_name()[:8]:<{8}} '
                  f'DMG:{c.get_damage():> {4}}/??? '
                  f'SP:{c.get_sp():>+{3}}')
            ci += 1

