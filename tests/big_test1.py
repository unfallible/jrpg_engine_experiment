import json
from pprint import PrettyPrinter

from JrpgBattle.Character import CharacterStatus
from JrpgBattle.ConcretePlayerServer import InteractivePlayerServer
from JrpgBattle.IdentifierSet import IdentifierSet
from JrpgBattle.JsonProcessing.JrpgEncoder import JrpgDataManager
from JrpgBattle.MainBattleClient import MainBattleClient
from JrpgBattle.Party import Party

if __name__ == '__main__':
    manager = JrpgDataManager()
    pp = PrettyPrinter(indent=2)
    with open('data\\VanillaAttacks.json', 'r') as f:
        # data = f.read().replace('\n', '')
        data = f.read()
        attacks = json.loads(data, object_hook=manager.get_jrpg_decoder_func())
        pp.pprint(attacks)
    pp.pprint(f'Attack cache: {str(manager.attack_cache)}')
    # print(str([manager.attack_cache[atk_name] for atk_name in data['attack_list']]))
    with open('data\\CharacterTemplates.json', 'r') as f:
        data = f.read().replace('\n', '')
        characters = json.loads(data, object_hook=manager.get_jrpg_decoder_func())
        pp.pprint(characters)
    terra = CharacterStatus(manager.character_cache["somebody"], "terra")
    cloud = CharacterStatus(manager.character_cache["somebody"], "cloud")
    party_1 = Party("player 1", {terra})
    party_2 = Party("player 2", {cloud})
    idset = IdentifierSet[CharacterStatus]({terra, cloud})
    player_server = InteractivePlayerServer()
    battle_client = MainBattleClient()
    battle_client.register_party(party_1, player_server)
    battle_client.register_party(party_2, player_server)
    battle_client.start_battle()
