from typing import List, Tuple

from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.CharacterViews import PrivateCharacterView, PublicCharacterView
from JrpgBattle.GameManagement.MainBattleClient import PlayerServer, BattleClient
from JrpgBattle.Party import Party
from JrpgBattle.Attack import Attack, AttackPlan


class SimpleInteractivePlayerServer(PlayerServer):
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

            keep_going = True
            while keep_going:
                raw_input = input('Attack? (y/n):\n')
                try:
                    if raw_input.strip() == "y":
                        attacks: List[AttackPlan] = [AttackPlan(indexed_team[0],
                                                                indexed_attacks[0][0],
                                                                {indexed_enemy[0]})]
                        keep_going = False
                    elif raw_input.strip() == "n":
                        attacks: List[AttackPlan] = []
                        keep_going = False
                    else:
                        print(f'Invalid input: {raw_input}')
                except Exception:
                    print(f'Invalid input: {raw_input}')

            keep_going = True
            while keep_going:
                raw_input = input('Defend? (y/n):\n')
                try:
                    if raw_input.strip() == "y":
                        defenses = {indexed_team[0]: indexed_team[0]}
                        keep_going = False
                    elif raw_input.strip() == "n":
                        defenses = {}
                        keep_going = False
                    else:
                        print(f'Invalid input: {raw_input}')
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
            # guard_value = "MAX" if not c.get_guard() else str(-1 * c.get_guard())
            guard_value = f'{float(c.get_guard()):.1%}'
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
            # guard_value = "MAX" if not c.get_guard() else str(-1 * c.get_guard())
            guard_value = f'{float(c.get_guard()):.1%}'
            next_attack = c.get_next_attack().name if c.get_next_attack() is not None else "???"
            print(f'{f"{ci:}.":<{3}}  {c.get_character_name()[:8]:<{8}} '
                  f'DMG:{c.get_damage():> {4}}/??? '
                  f'SP:{c.get_sp():>+{3}}  GRD:{guard_value}\n'
                  f'    VIS: {c.get_visibility()}  NEXT: {next_attack}')
            ci += 1
