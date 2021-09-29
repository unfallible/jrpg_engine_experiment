"""
The BattleClient class runs the main game loop for the battle system.
It maintains a list of each player of the game, and their respective parties and their PlayerServer.
When the game reaches a point where player input is required, the BattleClient sends the PlayerServer
a request containing their "view" of the game state and the action requested. When the PlayerServer receives
the request, it processes it and sends a response containing the requested action.
"""

from typing import Dict, List
from abc import ABC, abstractmethod

from JrpgBattle import Party, Attack
from JrpgBattle.Character import CharacterStatus


class BattleClient(ABC):
    @abstractmethod
    def process_action_response(self,
                                response: List[Attack],
                                defense: Dict[CharacterStatus, CharacterStatus],
                                transaction_id: int):
        pass


class PlayerServer(ABC):
    @abstractmethod
    def process_action_request(self,
                               client: BattleClient,
                               transaction_id: int):
        pass


class MainBattleClient(BattleClient):
    def __init__(self,
                 roster: Dict[Party, PlayerServer]={}):
        self.roster = roster
        self.transaction_count = 0
        self._transaction_in_progress = False

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
                self._transaction_in_progress = True
                party.attack_queue = self.roster[party].process_action_request(self,
                                                                               self.transaction_count)
                while self._transaction_in_progress:
                    continue
                self.transaction_count += 1

                turn += 1
                for party in self.roster:
                    if party.is_wiped_out():
                        pass  # TODO: Implement logic for finishing game
            round += 1

    def process_action_response(self,
                                attacks: Attack,
                                defense: Dict[CharacterStatus,CharacterStatus],
                                transaction_id: int):
        pass
