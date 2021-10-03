from typing import List, Tuple

from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.CharacterViews import PrivateCharacterView, PublicCharacterView
from JrpgBattle.MainBattleClient import PlayerServer, BattleClient
from JrpgBattle.Party import Party
from JrpgBattle.Attack import Attack, AttackPlan


class InteractivePlayerServer(PlayerServer):
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
        self.team = team
        indexed_team = [char for char in team]
        indexed_attacks = [[atk for atk in char.get_attack_list()] for char in indexed_team]

        self.enemy = enemy
        indexed_enemy = [char for char in enemy]

        tokens = input('Attacks? "(format user_index,attack_index,enemy_index")').split()
        attack_indexes = [[int(index) - 1 for index in act.split(',') if index] for act in tokens]
        attacks: List[AttackPlan] = [AttackPlan(indexed_team[i[0]],
                                                indexed_attacks[i[0]][i[1]],
                                                {indexed_enemy[x] for x in i[2:]}) for i in attack_indexes]

        tokens = input('Defenses? (format "defender_index,target_index")').split()
        defense_indexes = [[int(index) - 1 for index in act.split(',') if index] for act in tokens]
        defenses = {indexed_team[i[0]]: indexed_team[i[1]] for i in defense_indexes}

        client.process_command_response(attacks=attacks, defenses=defenses, transaction_id=transaction_id)

    # def process_view_response(self,
    #                           team: PrivatePartyView,
    #                           enemy: PublicPartyView,
    #                           transaction_id: int) -> int:
    #     assert transaction_id in self.open_requests
    #     self.team = team
    #     self.team_index = [(char, [atk for atk in char.get_attack_list()]) for char in team]
    #     # for char in team:
    #     #     self.team_index.append((char, [atk for atk in char.get_attack_list()]))
    #     self.enemy = enemy
    #     self.enemy_index = [char for char in enemy]
    #     self.open_requests.discard(transaction_id)
    #     return PlayerServer.SUCCESS

    def _print_player_view(self, team: List[PrivateCharacterView],
                           attacks: List[Attack], enemy: List[PublicCharacterView]):
        assert len(team) == len(attacks)
        print(f'Team {self.team.name[:8]}:')
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
        ci = 1
        print('ENEMIES:')
        for c in enemy:
            print(f'{f"{ci}.":<{3}}  {c.get_character_name()[:8]:<{8}} '
                  f'DMG:{c.get_damage():> {4}}/??? '
                  f'SP:{c.get_sp():>+{3}}')
            ci += 1
