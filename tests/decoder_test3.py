import json
from pprint import PrettyPrinter

from JrpgBattle.JsonProcessing.JrpgEncoder import decode_jrpg_data, JrpgDataManager

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
