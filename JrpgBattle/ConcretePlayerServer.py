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
        client_rval = BattleClient.ERROR
        while client_rval == BattleClient.ERROR:
            self.team = team
            indexed_team = [char for char in team]
            indexed_attacks = [[atk for atk in char.get_attack_list()] for char in indexed_team]
            self.enemy = enemy
            indexed_enemy = [char for char in enemy]

            self._print_player_view(indexed_team, indexed_attacks, indexed_enemy)

            keep_going = False
            while not keep_going:
                raw_input = input('Attacks? (format "user_index,attack_index,enemy_index")\n')
                try:
                    tokens = raw_input.split()
                    attack_indexes = [[int(index) - 1 for index in act.split(',') if index] for act in tokens]
                    attacks: List[AttackPlan] = [AttackPlan(indexed_team[i[0]],
                                                            indexed_attacks[i[0]][i[1]],
                                                            {indexed_enemy[x] for x in i[2:]}) for i in attack_indexes]
                    keep_going = True
                except Exception:
                    print(f'Invalid input: {raw_input}')

            keep_going = False
            while not keep_going:
                raw_input = input('Defenses? (format "defender_index,target_index")\n')
                try:
                    tokens = raw_input.split()
                    defense_indexes = [[int(index) - 1 for index in act.split(',') if index] for act in tokens]
                    defenses = {indexed_team[i[0]]: indexed_team[i[1]] for i in defense_indexes}
                    keep_going = True
                except Exception:
                    print(f'Invalid input: {raw_input}')

            client_rval = client.process_command_response(attacks=attacks, defenses=defenses, transaction_id=transaction_id)
        return PlayerServer.SUCCESS

    def _print_player_view(self, team: List[PrivateCharacterView],
                           attacks: List[List[Attack]], enemy: List[PublicCharacterView]):
        assert len(team) == len(attacks)
        # print(f'Team {self.team.name[:8]}:')
        print('TEAM:')
        ci = 1
        for c in team:
            # the nested f string concatenates 'ci' with '.' and then left justifies it
            print(f'{f"{ci}.":<{3}} {c.get_character_name()[:8]:<{8}} '
                  f'HP:{f"{c.get_current_hp()}/{c.get_max_hp()}":<{8}} '
                  f'SP:{c.get_sp():<+{3}}')
            ai = 1
            for a in c.get_attack_list():
                print(f'    {ai:>{2}}.  {a.name[:8]:<{8}} STR:{a.get_power():<{3}} SP:{a.stamina_point_cost:<{3}}')
                ai += 1
            ci += 1
        ci = 1
        print('ENEMIES:')
        for c in enemy:
            print(f'{f"{ci:}.":<{3}}  {c.get_character_name()[:8]:<{8}} '
                  f'DMG:{c.get_damage():> {4}}/??? '
                  f'SP:{c.get_sp():>+{3}}')
            ci += 1
