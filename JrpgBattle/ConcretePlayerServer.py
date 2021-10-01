from typing import Dict, List
from abc import ABC, abstractmethod

from JrpgBattle import Party, Attack
from JrpgBattle.Character import CharacterStatus
from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.CharacterViews import PrivateCharacterView, PublicCharacterView
from JrpgBattle.MainBattleClient import PlayerServer, BattleClient
from JrpgBattle.Party import PartyIdentifier

class InteractivePlayerServer(PlayerServer):
    def __int__(self,
                client: BattleClient):
        self.team: PrivatePartyView = None
        self.enemy: PublicPartyView = None
        self.open_request: bool = False

    def process_action_request(self,
                               client: BattleClient,
                               party_id: PartyIdentifier,
                               transaction_id: int):

        pass

    def process_team_response(self,
                              team: PrivatePartyView,
                              client: BattleClient,
                              transaction_id: int) -> int:
        pass

    def process_enemy_response(self,
                               enemy: PublicPartyView,
                               client: BattleClient,
                               transaction_id: int) -> int:
        pass

    def _print_player_view(self, team: PrivatePartyView, enemy: PublicPartyView):
        print(f'Team {team.name[:8]}:')
        ci = 1
        for c in team:
            print(f'{ci:>{2}}.  {c.get_character_name()[:8]:<{8}} '
                  f'HP:{c.get_current_hp():>{3}}/{c.get_max_hp():<{3}} '
                  f'SP:{c.get_sp():>+{3}}')
            ai = 1
            for a in c.get_attack_list():
                print(f'    {ai:>{2}}.  {a.name[:8]:<{8}} SP:{a.stamina_point_cost:<+{3}}')
                ai += 1
            ci += 1
        print('ENEMIES:')
        for c in enemy:
            print(f'{ci:>{2}}.  {c.get_character_name()[:8]:<{8}} '
                  f'DMG:{c.get_damage():> {4}}/??? '
                  f'SP:{c.get_sp():>+{3}}')
            ci += 1


        print('Player: ' + team.name)
