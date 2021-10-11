"""
The BattleClient class runs the main game loop for the battle system.
It maintains a list of each player of the game, and their respective roster and their PlayerServer.
When the game reaches a point where player input is required, the BattleClient sends the PlayerServer
a request containing their "view" of the game state and the action requested. When the PlayerServer receives
the request, it processes it and sends a attacks containing the requested action.
"""

from __future__ import annotations
from typing import Dict, List
from abc import ABC, abstractmethod

from JrpgBattle.BattleEventHandling.EventManagement import EventObserver, E
from JrpgBattle.Party import Party, PartyIdentifier
from JrpgBattle.Character import CharacterStatus, CharacterIdentifier
from JrpgBattle.PartyViews import PrivatePartyView, PublicPartyView
from JrpgBattle.Attack import AttackPlan, AttackQueue, DetailedAttackPlan


class BattleClient(ABC):
    SUCCESS = 0
    ERROR = 1

    @abstractmethod
    def process_command_response(self,
                                 attacks: List[AttackPlan],
                                 defenses: Dict[CharacterIdentifier, CharacterIdentifier],
                                 transaction_id: int):
        pass

    # @abstractmethod
    # def process_view_request(self,
    #                          server: PlayerServer,
    #                          transaction_id: int):
    #     pass


class PlayerServer(ABC):
    SUCCESS = 0
    ERROR = 1

    @abstractmethod
    def process_command_request(self,
                                client: BattleClient,
                                transaction_id: int,
                                team: PrivatePartyView,
                                enemy: PublicPartyView) -> int:
        pass

    # @abstractmethod
    # def process_view_response(self,
    #                           team: PrivatePartyView,
    #                           enemy: PublicPartyView,
    #                           transaction_id: int) -> int:
    #     pass


class PlayerProfile:
    def __init__(self, player_id: int, party: Party, server: PlayerServer):
        self.party = party
        self.server = server

    def __eq__(self, other):
        return isinstance(other, PlayerProfile) and self.party == other.party

    def __hash__(self):
        return hash(self.party)


class MainBattleClient(BattleClient, EventObserver):
    # def __init__(self,
    #              roster: Set[Tuple[Party, PlayerServer]] = set()):
    def __init__(self):
        EventObserver.__init__(self)
        self.roster: List[PlayerProfile] = []
        self.characters_ids: Dict[CharacterIdentifier, CharacterStatus] = {}
        self.party_ids: Dict[PartyIdentifier, Party] = {}
        self.transaction_count = 0
        self.open_transactions: Dict[int, Party] = {}

    def register_party(self, party: Party, server: PlayerServer) -> int:
        # TODO CON: is the assignment of player ids here safe?
        new_player = PlayerProfile(len(self.roster), party, server)
        if new_player in self.roster or set(party.characters) & set(self.characters_ids):
            return BattleClient.ERROR
        self.roster.append(new_player)
        self.party_ids[party] = party
        # TODO: Find better way to add the character ids
        # for character in party.characters:
        for character in party.characters:
            self.characters_ids[character] = character
            character.register_observer(self)
        return BattleClient.SUCCESS

    """
    Runs the game loop for the battle system. 
    This loop is separate from the main game loop, which will run in real time and handle player IO.
    The expectation is that main game loop will communicate with the BattleClient via the PlayerServer
    interface. 
    """

    def handle_event(self, event: E) -> bool:
        print(f'Event occurred: {str(event)}')

    def start_battle(self):
        battle_round = 1
        turn = 1
        winner = None
        while winner is None:
            # loop every player once per round
            for player in self.roster:
                team = player.party
                # start turn by executing existing plans
                for member in team:
                    member.start_turn()

                for plan in team.attack_queue:
                    plan.execute()

                for member in player.party:
                    member.turn_interval()
                # once existing plans have been executed, the player plans their next turn
                self.open_transactions[self.transaction_count] = player.party  # open transaction for the player
                # TODO FEAT: support more than two registered players
                enemy = next(opponent.party for opponent in self.roster if not team == opponent.party)
                while player.server.process_command_request(self,
                                                            self.transaction_count,
                                                            PrivatePartyView(team),
                                                            PublicPartyView(enemy)) != PlayerServer.SUCCESS:
                    continue
                while self.open_transactions:
                    continue
                self.transaction_count += 1

                turn += 1
                for player in self.roster:
                    if player.party.is_wiped_out():
                        # TODO: Implement logic for finishing game
                        self.roster.remove(player)
                        if len(self.roster) == 1:
                            winner = self.roster[0]
                            print(f'{winner.party.name} wins!')
            battle_round += 1

    def process_command_response(self,
                                 attacks: List[AttackPlan],
                                 defenses: Dict[CharacterIdentifier, CharacterIdentifier],
                                 transaction_id: int) -> int:
        new_plans: AttackQueue = AttackQueue()
        for plan in attacks:
            # first validate each plan
            if self.validate_attack_plan(plan, self.open_transactions[transaction_id]):
                # if the plan is valid, add queue it up for next turn
                detailed_plan = DetailedAttackPlan(plan.attack,
                                                   self.characters_ids[plan.user],
                                                   {self.characters_ids[target] for target in plan.targets})
                new_plans.enqueue(detailed_plan)
            else:
                # if the plan is invalid, return an error
                return BattleClient.ERROR
        # set defenses
        for char_id in defenses:
            target = self.characters_ids[defenses[char_id]]
            self.characters_ids[char_id].set_defense(target)
        # now look up the party associated with the action request
        party = self.open_transactions[transaction_id]
        # set the party's plans for next turn, then close the transaction
        party.attack_queue = new_plans
        self.open_transactions.pop(transaction_id)
        return BattleClient.SUCCESS

    # def process_view_request(self,
    #                          server: PlayerServer,
    #                          transaction_id: int):
    #     team = next(profile.party for profile in self.roster if profile.server is server)
    #     team_view = PrivatePartyView(team)
    #     enemy = next(profile.party for profile in self.roster if profile.server is not server)
    #     enemy_view = PublicPartyView(enemy)
    #     rval = server.process_view_response(team_view, enemy_view, transaction_id)
    #     return rval

    def validate_attack_plan(self, plan: AttackPlan, user_party: Party) -> bool:
        # It is ESSENTIAL that attack validation only uses information available to the player who set the plan
        if plan.user not in user_party:
            return False
        # user_status = user_party.get_status(plan.attacker)
        user_status = self.characters_ids[plan.user]
        if plan.attack not in user_status.get_attack_list():
            return False
        # TODO: This loop is pretty harmless but it looks really gross
        # TODO: Consider adding logic to the Attack and Character classes to perform some validation
        for target in plan.targets:
            for player in self.roster:
                if user_party is not player.party and target in player.party:
                    return True
        return False


