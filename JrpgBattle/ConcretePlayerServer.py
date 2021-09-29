from typing import Dict, List
from abc import ABC, abstractmethod

from JrpgBattle import Party, Attack
from JrpgBattle.Character import CharacterStatus
from JrpgBattle.MainBattleClient import PlayerServer, BattleClient

class InteractivePlayerServer(PlayerServer):
    def __int__(self):
        pass

    def process_action_request(self,
                               client: BattleClient,
                               transaction_id: int):
        pass

    def _print_player_view(self, client: BattleClient):
        print('Player: ' + )
