from typing import List, Tuple

from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.CharacterViews import PrivateCharacterView, PublicCharacterView
from JrpgBattle.GameManagement.MainBattleClient import PlayerServer, BattleClient
from JrpgBattle.Party import Party
from JrpgBattle.Attack import Attack, AttackPlan


class AggroNonPlayerServer(PlayerServer):
    def __init__(self):
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
            for character in team:
                if character.get_sp() == 0:
                    continue
                attacks.append(AttackPlan(character,
                                          next(iter(character.get_attack_list())),
                                          {next(iter(enemy))}))
            defenses = {}
            client_rval = client.process_command_response(attacks=attacks, defenses=defenses, transaction_id=transaction_id)
        return PlayerServer.SUCCESS

    def _print_player_view(self, team: List[PrivateCharacterView],
                           attacks: List[List[Attack]], enemy: List[PublicCharacterView]):
        assert len(team) == len(attacks)
        # print(f'Team {self.team.name[:8]}:')
        print('TEAM:')
        ci = 1
        for c in team:
            guard_value = "MAX" if not c.get_vulnerability() else str(-1*c.get_vulnerability())
            # the nested f string concatenates 'ci' with '.' and then left justifies it
            print(f'{f"{ci}.":<{3}} {c.get_character_name()[:8]:<{8}} '
                  f'HP:{f"{c.get_current_hp()}/{c.get_max_hp()}":<{8}} '
                  f'SP:{c.get_sp():<+{3}}  GRD:{guard_value}')
            ai = 1
            for a in c.get_attack_list():
                print(f'    {ai:>{2}}.  {a.name[:8]:<{8}} STR:{a.get_power():<{3}} SP:{a.stamina_point_cost:<{3}}')
                ai += 1
            ci += 1
        ci = 1
        print('ENEMIES:')
        for c in enemy:
            guard_value = "MAX" if not c.get_vulnerability() else str(-1*c.get_vulnerability())
            print(f'{f"{ci:}.":<{3}}  {c.get_character_name()[:8]:<{8}} '
                  f'DMG:{c.get_damage():> {4}}/??? '
                  f'SP:{c.get_sp():>+{3}}  GRD:{guard_value}')
            ci += 1
