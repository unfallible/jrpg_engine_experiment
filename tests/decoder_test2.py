import json
from pprint import PrettyPrinter

from JrpgBattle.JsonProcessing.JrpgEncoder import decode_jrpg_data

if __name__ == '__main__':
    with open('data\\VanillaAttacks.json', 'r') as f:
        data = f.read().replace('\n', '')
        attacks = json.loads(data, object_hook=decode_jrpg_data)
        pp = PrettyPrinter(indent=2)
        pp.pprint(attacks)
