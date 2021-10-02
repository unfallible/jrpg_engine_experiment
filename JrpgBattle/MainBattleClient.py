"""
The BattleClient class runs the main game loop for the battle system.
It maintains a list of each player of the game, and their respective roster and their PlayerServer.
When the game reaches a point where player input is required, the BattleClient sends the PlayerServer
a request containing their "view" of the game state and the action requested. When the PlayerServer receives
the request, it processes it and sends a response containing the requested action.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Set
from abc import ABC, abstractmethod

from JrpgBattle.Party import Party, PartyIdentifier
from JrpgBattle.Character import CharacterStatus, CharacterIdentifier, CharacterTemplate
from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.Attack import AttackPlan, AttackQueue, DetailedAttackPlan


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
                               party_id: PartyIdentifier,
                               transaction_id: int) -> int:
        pass

    @abstractmethod
    def process_team_response(self,
                              team: PrivatePartyView,
                              transaction_id: int) -> int:
        pass

    @abstractmethod
    def process_enemy_response(self,
                               enemy: PublicPartyView,
                               transaction_id: int) -> int:
        pass


class PlayerProfile:
    def __init__(self, player_id: int, party: Party, server: PlayerServer):
        self.party = party
        self.server = server

    def __eq__(self, other):
        return isinstance(other, PlayerProfile) and self.party == other.party

    def __hash__(self):
        return hash(self.party)


class MainBattleClient(BattleClient):
    # def __init__(self,
    #              roster: Set[Tuple[Party, PlayerServer]] = set()):
    def __init__(self):
        self.roster: List[PlayerProfile] = []
        self.characters_ids: Dict[CharacterIdentifier, CharacterStatus] = {}
        self.party_ids: Dict[PartyIdentifier, Party] = {}
        self.transaction_count = 0
        self.open_transactions: Dict[int, Party] = {}

    def register_party(self, party: Party, server: PlayerServer) -> int:
        new_player = PlayerProfile(party, server)
        if new_player in self.roster or set(party.characters) & set(self.characters_ids):
            return BattleClient.ERROR
        self.roster.append(new_player)
        self.party_ids[party] = party
        # TODO: Find better way to add the character ids
        for character in party:
            self.characters_ids[character] = character
        return BattleClient.SUCCESS

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
            for player in self.roster:
                # start turn by executing existing plans
                for member in player.party:
                    member.start_turn()

                for plan in player.party.attack_queue:
                    plan.execute()

                for member in player.party:
                    member.turn_interval()
                # once existing plans have been executed, the player plans their next turn
                self.open_transactions[self.transaction_count] = self.roster[party]  # open transaction for the player
                party.attack_queue = player.server.process_action_request(self, self.transaction_count)
                while self.open_transactions:
                    continue
                self.transaction_count += 1

                turn += 1
                for party in self.roster:
                    if party.party.is_wiped_out():
                        pass  # TODO: Implement logic for finishing game
            round += 1

    def process_action_response(self,
                                response: List[AttackPlan],
                                defense: Dict[CharacterIdentifier, CharacterIdentifier],
                                transaction_id: int) -> int:
        new_plans: AttackQueue = AttackQueue()
        for plan in response:
            # first validate each plan
            if self.validate_attack_plan(plan):
                self.validate_attack_plan(plan, self.open_transactions[transaction_id])
                # if the plan is valid, add queue it up for next turn
                detailed_plan = DetailedAttackPlan(plan.attack,
                                                   self.characters_ids[plan.user],
                                                   {self.characters_ids[target] for target in plan.targets})
                new_plans.enqueue(detailed_plan)
            else:
                # if the plan is invalid, return an error
                return BattleClient.ERROR
        # now look up the party associated with the action request
        party = self.players[self.open_transactions[transaction_id]]
        # set the party's plans for next turn, then close the transaction
        party.attack_queue = new_plans
        self.open_transactions.pop(transaction_id)
        return BattleClient.SUCCESS

    def process_team_request(self,
                             server: PlayerServer,
                             transaction_id: int):
        team = next(profile.party for profile in self.roster if profile.server is server)
        team_view = PrivatePartyView(team)
        rval = server.process_team_response(team_view, transaction_id)
        return rval

    def process_enemy_request(self,
                              server: PlayerServer,
                              transaction_id: int):
        enemy = next(profile.party for profile in self.roster if profile.server is server)
        enemy_view = PublicPartyView(enemy)
        rval = server.process_enemy_response(enemy_view, transaction_id)
        return rval

    def validate_attack_plan(self, plan: AttackPlan, user_party: Party) -> bool:
        # It is ESSENTIAL that attack validation only uses information available to the player who set the plan
        if plan.user not in user_party:
            return False
        # user_status = user_party.get_status(plan.user)
        user_status = self.characters_ids[plan.user]
        if plan.attack not in user_status.get_attack_list():
            return False
        # TODO: This loop is pretty harmless but it looks really gross
        # TODO: Consider adding logic to the Attack and Character classes to perform some validation
        for target in plan.targets:
            for party in self.roster:
                if target not in party:
                    return False
        return True
