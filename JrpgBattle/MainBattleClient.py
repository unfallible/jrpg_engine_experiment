"""
The BattleClient class runs the main game loop for the battle system.
It maintains a list of each player of the game, and their respective parties and their PlayerServer.
When the game reaches a point where player input is required, the BattleClient sends the PlayerServer
a request containing their "view" of the game state and the action requested. When the PlayerServer receives
the request, it processes it and sends a response containing the requested action.
"""

from typing import Dict
from abc import ABC, abstractmethod

from JrpgBattle import Party, Attack
from JrpgBattle.Character import CharacterStatus


class BattleClient(ABC):
    @abstractmethod
    def receive_action_response(self,
                                response: Attack,
                                server: PlayerServer,
                                transaction_id: int):
        pass


class PlayerServer(ABC):
    @abstractmethod
    def receive_action_request(self,
                               client: BattleClient,
                               transaction_id: int):
        pass


class MainBattleClient(BattleClient):
    def __init__(self,
                 roster: Dict[Party, PlayerServer]={}):
        self.roster = roster
        self.transaction_count = 0

    """
    Runs the game loop for the battle system
    """
    def start_battle(self):
        round = 1
        turn = 1
        while True:
            # loop every player once per round
            for party in self.roster:
                # start turn by executing existing plans
                for member in party:
                    member.start_turn()

                for plan in party.attack_queue:
                    plan.execute()

                for member in party:
                    member.turn_interval()
                # once existing plans have been executed, the player plans their next turn
                party.attack_queue = self.roster[party].receive_action_request(self,
                                                                               self.transaction_count)
                self.transaction_count += 1
                turn += 1
            round += 1

    def receive_action_response(self,
                                attacks: Attack,
                                defense: Dict[CharacterStatus,CharacterStatus],
                                server: PlayerServer,
                                transaction_id: int):
        pass




class PlayerView:
    def __int__(self):
        pass
