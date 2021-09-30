"""
The BattleClient class runs the main game loop for the battle system.
It maintains a list of each player of the game, and their respective parties and their PlayerServer.
When the game reaches a point where player input is required, the BattleClient sends the PlayerServer
a request containing their "view" of the game state and the action requested. When the PlayerServer receives
the request, it processes it and sends a response containing the requested action.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Set
from abc import ABC, abstractmethod

from JrpgBattle.Party import Party
from JrpgBattle.Character import CharacterStatus, CharacterIdentifier, CharacterTemplate
from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.Attack import AttackPlan, AttackQueue


class BattleClient(ABC):
    SUCCESS = 0
    ERROR = 1

    @abstractmethod
    def process_action_response(self,
                                response: List[AttackPlan],
                                defense: Dict[CharacterIdentifier, CharacterIdentifier],
                                transaction_id: int):
        pass

    @abstractmethod
    def process_team_request(self,
                             server: PlayerServer,
                             transaction_id: int):
        pass

    @abstractmethod
    def process_enemy_request(self,
                              server: PlayerServer,
                              transaction_id: int):
        pass


class PlayerServer(ABC):
    SUCCESS = 0
    ERROR = 1

    @abstractmethod
    def process_action_request(self,
                               client: BattleClient,
                               transaction_id: int) -> int:
        pass

    @abstractmethod
    def process_team_response(self,
                              team: PrivatePartyView,
                              client: BattleClient,
                              transaction_id: int) -> int:
        pass

    @abstractmethod
    def process_enemy_response(self,
                               enemy: PublicPartyView,
                               client: BattleClient,
                               transaction_id: int) -> int:
        pass


class MainBattleClient(BattleClient):
    def __init__(self,
                 roster: Dict[Party, PlayerServer] = {}):
        self.parties = roster
        self.players = {roster[party]: party for party in roster}
        assert len(self.players) == len(self.parties)
        self.transaction_count = 0
        self.open_transactions: Dict[int, Party] = {}

    """
    Runs the game loop for the battle system. 
    This loop is separate from the main game loop, which will run in real time and handle player IO.
    The expectation is that main game loop will communicate with the BattleClient via the PlayerServer
    interface. 
    """
    def start_battle(self):
        round = 1
        turn = 1
        while True:
            # loop every player once per round
            for party in self.parties:
                # start turn by executing existing plans
                for member in party:
                    member.start_turn()

                for plan in party.attack_queue:
                    plan.execute()

                for member in party:
                    member.turn_interval()
                # once existing plans have been executed, the player plans their next turn
                self.open_transactions[self.transaction_count] = self.parties[party]  # open transaction for the player
                party.attack_queue = self.parties[party].process_action_request(self, self.transaction_count)
                while self.open_transactions:
                    continue
                self.transaction_count += 1

                turn += 1
                for party in self.parties:
                    if party.is_wiped_out():
                        pass  # TODO: Implement logic for finishing game
            round += 1

    def process_action_response(self,
                                response: List[AttackPlan],
                                defense: Dict[CharacterIdentifier, CharacterIdentifier],
                                transaction_id: int) -> int:
        party = self.players[self.open_transactions[transaction_id]]
        new_plans: AttackQueue = AttackQueue()
        for plan in response:
            if self.validate_attack_plan(plan):
                pass
            else:
                return BattleClient.ERROR
        party.attack_queue = new_plans
        self.open_transactions.pop(transaction_id)
        return BattleClient.SUCCESS

    def validate_attack_plan(self, plan: AttackPlan, user_party: Party) -> bool:
        # It is ESSENTIAL that attack validation only uses information available to the player who set the plan
        if plan.user not in user_party:
            return False
        user_status = user_party.get_status(plan.user)
        if plan.attack not in user_status.get_attack_list():
            return False
        # TODO: This loop is pretty harmless but it looks really gross
        # TODO: Consider adding logic to Attacks and Character to perform some validation
        for target in plan.targets:
            for party in self.parties:
                if target not in party:
                    return False
        return True
