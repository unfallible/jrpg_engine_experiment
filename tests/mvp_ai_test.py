import json
import logging
from pprint import PrettyPrinter

from JrpgBattle.Character import CharacterStatus
from JrpgBattle.GameManagement.MinimumViablePlayerServer import SimpleInteractivePlayerServer
from JrpgBattle.GameManagement.NonPlayerServers import AggroNonPlayerServer
from JrpgBattle.IdentifierSet import IdentifierSet
from JrpgBattle.JsonProcessing.JrpgEncoder import JrpgDataManager
from JrpgBattle.GameManagement.MainBattleClient import MainBattleClient
from JrpgBattle.Party import Party

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO,
    #                     format="%(message)s",
    #                     handlers=[logging.StreamHandler()])
    manager = JrpgDataManager()
    # pp = PrettyPrinter(indent=2)
    with open('data\\VanillaAttacks.json', 'r') as f:
        # data = f.read().replace('\n', '')
        data = f.read()
        attacks = json.loads(data, object_hook=manager.get_jrpg_decoder_func())
        # pp.pprint(attacks)
    # pp.pprint(f'Attack cache: {str(manager.attack_cache)}')
    # print(str([manager.attack_cache[atk_name] for atk_name in data['attack_list']]))
    with open('data\\CharacterTemplates.json', 'r') as f:
        data = f.read().replace('\n', '')
        characters = json.loads(data, object_hook=manager.get_jrpg_decoder_func())
        # pp.pprint(characters)
    terra = CharacterStatus(manager.character_cache["somebody"], "Terra")
    mad_dog = CharacterStatus(manager.character_cache["somebody"], "Mad Dog")
    mad_dog.current_sp = 9999
    party_1 = Party("PLAYER", {terra})
    party_2 = Party("ENEMY", {mad_dog})
    idset = IdentifierSet[CharacterStatus]({terra, mad_dog})
    player_server = SimpleInteractivePlayerServer()
    non_player_server = AggroNonPlayerServer()
    battle_client = MainBattleClient()
    battle_client.register_party(party_1, player_server)
    battle_client.register_party(party_2, non_player_server)
    battle_client.start_battle()
