from JrpgBattle.Attack import VanillaAttack, AttackType
from JrpgBattle.Character import CharacterTemplate
from JrpgBattle.JsonProcessing.JrpgEncoder import decode_jrpg_data, encode_jrpg_data
from fractions import Fraction
import json


def main():
    atk1 = VanillaAttack('chocolate', damage=3)
    atk2 = VanillaAttack('strawberry', damage=5, stamina_point_cost=150)
    atk1_json = json.dumps(atk1, default=encode_jrpg_data)
    atk2_json = json.dumps(atk2, default=encode_jrpg_data)
    chocolate = json.loads(atk1_json, object_hook=decode_jrpg_data)
    strawberry = json.loads(atk2_json, object_hook=decode_jrpg_data)

    dude = CharacterTemplate(name='tyler', max_hp=10, offensive_type_affinities={}, defensive_type_affinities={},
                             attack_list={chocolate, strawberry}, parry_effectiveness=Fraction(3, 4))
    print(json.dumps(dude, default=encode_jrpg_data, indent=2))

if __name__ == '__main__':
    main()
